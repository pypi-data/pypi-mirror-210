import os
import torch
import torch.nn 
from torch.autograd import Variable
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
import time
from torch.utils.data import DataLoader
from PIL import Image
import cv2



warnings.filterwarnings('ignore')

def pth_info(checkpoint):
    ckpt = torch.load(checkpoint,map_location='cpu')
    meta = ckpt['meta']
    m = list(meta.keys())
    if 'device' in m:
        m.insert(0,m.pop(m.index('device')))
    if 'backbone' in m:
        m.insert(0,m.pop(m.index('backbone')))
    if 'tool' in m:
        m.insert(0,m.pop(m.index('tool')))

    print(checkpoint,"相关信息如下:")
    print("="*(len(checkpoint)+9))
    for i in m:
        if i == 'word2idx': # 省略完整词表，只展示前10个词
            w2i = '{'
            for j in list(meta[i].keys())[:10]:
                w2i += str(j)+":"+str(meta[i][j])+","
            w2i += '...}'
            print(i,":",w2i)
        else:          
            print(i,":",meta[i])
    print("="*(len(checkpoint)+9))


class lstm(torch.nn.Module):
    def __init__(self, vocab_size, embedding_dim, hidden_dim, num_layers):
        super(lstm, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.embedding = torch.nn.Embedding(vocab_size, embedding_dim)
        self.lstm = torch.nn.LSTM(embedding_dim, self.hidden_dim, num_layers=num_layers)
        self.linear = torch.nn.Linear(self.hidden_dim, vocab_size)

    def forward(self, input, hidden = None):
        seq_len, batch_size = input.size()
        
        if hidden is None:
            h_0 = input.data.new(self.num_layers, batch_size, self.hidden_dim).fill_(0).float()
            c_0 = input.data.new(self.num_layers, batch_size, self.hidden_dim).fill_(0).float()
        else:
            h_0, c_0 = hidden

        embeds = self.embedding(input)
#         print("embeds",embeds.shape)
        output, hidden = self.lstm(embeds, (h_0, c_0))
#         print("lstm",output.shape)
        output = self.linear(output.view(seq_len * batch_size, -1))
#         print("linear",output.shape,seq_len)

        return output, hidden

class Reshape(torch.nn.Module):
    def __init__(self, *args):
        super(Reshape, self).__init__()
        self.shape = args

    def forward(self, x):
        return x.contiguous().view(x.shape[0], -1)

class Part0(torch.nn.Module):
    def __init__(self, *args):
        super(Part0, self).__init__()
        self.shape = args

    def forward(self, x):
        # print("Part0", type(x), type(x[0]))
        return x[0]
    
class Unsqueeze(torch.nn.Module):
    def __init__(self, *args):
        super(Unsqueeze, self).__init__()

    def forward(self, x):
        # print("unsqueeze",type(x), type(x[:, -1, :].unsqueeze(1)))
        return x[:, -1, :].unsqueeze(1)
    
class Squeeze(torch.nn.Module):
    def __init__(self, *args):
        super(Squeeze, self).__init__()

    def forward(self, x):
        return x.squeeze()

def cal_accuracy(y, pred_y):
    res = pred_y.argmax(axis=1)
    tp = np.array(y.cpu())==np.array(res.cpu())
    acc = np.sum(tp)/ y.shape[0]
    return acc


class nn:
    def __init__(self, save_fold=None):
        self.model = torch.nn.Sequential()
        self.batchsize = None
        self.layers = []
        self.layers_num = 0
        self.optimizer = 'SGD'
        self.x = None
        self.y = None
        self.res = None
        self.save_fold = "checkpoints"
        self.rnn = False
        self.color = None # 若载入图片数据集，该变量表示灰度/RGB等颜色通道信息
        self.transform = None # 若载入图片数据集，该变量记录数据预处理操作
        if save_fold != None:
            self.save_fold = save_fold
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

 

    def add(self, layer=None, activation=None, optimizer=None, **kw):
        self.layers_num += 1
        self.layers.append(layer)
        if layer is not None and isinstance(layer,str):
            layer = layer.lower()
        if layer == 'linear':
            self.model.add_module('reshape', Reshape(self.batchsize))
            self.model.add_module('linear' + str(self.layers_num), torch.nn.Linear(kw['size'][0], kw['size'][1]))
            print("增加全连接层，输入维度:{},输出维度：{}。".format(kw['size'][0], kw['size'][1]))
        elif layer == 'reshape':
            self.model.add_module('reshape', Reshape(self.batchsize))
        # elif layer == 'ReLU':
        #     self.model.add_module('ReLU' + str(self.layers_num), nn.ReLU())
        #     print("增加ReLU层。")
        elif layer == 'conv2d':
            self.model.add_module('conv2d' + str(self.layers_num), torch.nn.Conv2d(kw['size'][0], kw['size'][1], kw['kernel_size']))
            print("增加二维卷积层，输入维度:{},输出维度：{},kernel_size: {} ".format(kw['size'][0], kw['size'][1], kw['kernel_size']))
        elif layer == 'conv1d':
            self.model.add_module('conv1d' + str(self.layers_num), torch.nn.Conv1d(kw['size'][0], kw['size'][1], kw['kernel_size']))
            print("增加一维卷积层，输入维度:{},输出维度：{},kernel_size: {} ".format(kw['size'][0], kw['size'][1], kw['kernel_size']))
        elif layer == 'maxpool':
            self.model.add_module('maxpooling' + str(self.layers_num), torch.nn.MaxPool2d(kw['kernel_size']))
            print("增加最大池化层,kernel_size: {} ".format(kw['kernel_size']))
        elif layer == 'avgpool':
            self.model.add_module('maxpooling' + str(self.layers_num), torch.nn.AvgPool2d(kw['kernel_size']))
            print("增加平均池化层,kernel_size: {} ".format(kw['kernel_size']))
        elif layer == 'dropout':
            p = 0.5 if 'p' not in kw.keys() else kw['p']
            self.model.add_module('dropout' + str(self.layers_num), torch.nn.Dropout(p=p) )
            print("增加dropout层,参数置零的概率为: {} ".format(p))
        elif layer =='em_lstm':
            self.rnn = True
            self.vs = len(self.word2idx)
            self.ed = kw['size'][0]
            self.hd = kw['size'][1]
            self.nl = kw['num_layers']
            # self.model.add_module('lstm', lstm(vs,ed,hd, nl))
            # self.model.add_module('LSTM' + str(self.layers_num), torch.nn.LSTM(kw['size'][0], kw['size'][1], kw['num_layers']))
            print("增加em_lstm层, 输入维度：{}, 输出维度：{}, 层数： {} ".format(kw['size'][0], kw['size'][1], kw['num_layers']))
            self.model =  lstm(self.vs,self.ed,self.hd, self.nl)
            self.model.to(self.device)
            self.config = {'model':'lstm','para':{'vs':self.vs,'ed':self.ed,'hd':self.hd,'nl':self.nl}}
        elif layer == 'lstm':
            l = torch.nn.LSTM(kw['size'][0], kw['size'][1], batch_first=True, bidirectional=False)
            l = l.to(self.device)
            self.model.add_module('lstm' + str(self.layers_num),  l)
            self.model.add_module("part0"+str(self.layers_num), Part0())
            print("增加lstm层, 输入维度：{}, 输出维度：{},".format(kw['size'][0], kw['size'][1]))
        elif layer == 'batchnorm1d':
            self.model.add_module('batchnorm1d'+str(self.layers_num),  torch.nn.BatchNorm1d(kw['size']))
            print("增加batchnorm层, 维度：{}".format(kw['size']))
        elif layer == "squeeze":
            self.model.add_module("squeeze", Squeeze())
        elif layer == "unsqueeze":
            self.model.add_module("unsqueeze", Unsqueeze())
        elif layer == 'part0':
            self.model.add_module("part0"+str(self.layers_num), Part0())
        elif layer is not None and not isinstance(layer, str):
            print("增加自定义模块{}".format(layer))
            self.model.add_module(str(layer.__class__.__name__)+str(self.layers_num), layer)

        if activation is not None:
            activation = activation.lower()
            # 激活函数
            if activation == 'relu':
                self.model.add_module('relu' + str(self.layers_num), torch.nn.ReLU())
                print("使用relu激活函数。")
            # elif activation == 'softmax':
            else:
                self.model.add_module('softmax'+str(self.layers_num), torch.nn.Softmax())
                print('使用softmax激活函数。')

        # 优化器
        if optimizer != None:
            self.optimizer = optimizer

    def visual_feature(self, data, in1img=False, save_fold="layers"):
        if len(data.shape) == 1:
            data = np.reshape(data, (1,data.shape[0]))
            data = Variable(torch.tensor(np.array(data)).to(torch.float32))
            self.model.eval()
            f = open(os.path.join(save_fold,'layer_data.txt'), "w")
            str_data = ""
            act_layer = 0
            tra_layer = 0
            for num, i in enumerate(self.model):
                data = i(data)
                # print(num, i, data)
                if isinstance(i, (type(torch.nn.ReLU()),type(torch.nn.Softmax()))): # 非传统层，不计数
                    act_layer+=0.1
                    str_data += str(tra_layer-1+act_layer) + "."+str(i) +"\n" + str(np.squeeze(data).tolist()) + "\n"
                else:  #传统网络层
                    act_layer =0
                    str_data += str(tra_layer) + "."+str(i) +"\n" + str(np.squeeze(data).tolist()) + "\n"
                    tra_layer+= 1


            f.write(str_data)
            f.close()
        else:
            if len(data.shape) == 2:
                h,w = data.shape
                c = 1
            elif  len(data.shape) == 3:
                h,w,c = data.shape
            data = np.reshape(data, (1,c,h,w))
            data = Variable(torch.tensor(np.array(data)).to(torch.float32))
            self.model.eval()
            dir_name = os.path.abspath(save_fold)
            if not os.path.exists(dir_name):
                os.mkdir(dir_name)
            if not in1img: # 每层分别画一张图，横向
                for num, i in enumerate(self.model):
                    data = i(data)
                    self.show_one_layer(data, i, num+1, dir_name)
            else: # 所有层共画一张图，纵向
                # fig, ax = plt.subplots(20, 20)
                plt.figure(figsize=(18,10))
                num_img = 0
                for name, para in self.model.named_parameters():
                    if "Linear" not in name:
                        num_img = max(num_img, para.size()[0])
                grid = plt.GridSpec(num_img+1,len(self.model)+1,wspace=0.5, hspace=0.5) #（ 单层最大图片数+1，层数）
                tra_layer = 1
                str_l = ""
                act_layer = 0
                for num, i in enumerate(self.model):
                    data = i(data)
                    tmp_data = data
                    # print(i,"data.shape", data.shape)
                    if len(data.shape) > 2 and data.shape[0] == 1:
                        tmp_data = np.squeeze(data)

                    for j in range(tmp_data.shape[0]): # 每一层
                        # print("num+1",num+1, "j", j)
                        img = tmp_data[j].detach().numpy()
                        if len(img.shape) == 1:
                            img = np.reshape(img, (img.shape[0],1))
                        # w, c = img.shape
                        # print(w, c)
                        # img = np.reshape(img, (w, c))
                        # plt.subplot(tmp_data.shape[0],num+1, j+1)
                        if tmp_data.shape[0] == 1:
                            # ax[:, num+1].imshow(img)
                            ax = plt.subplot(grid[1:, num+1])
                            ax.imshow(img)
                        else:
                            # ax[ j,num+1].imshow(img)
                            ax = plt.subplot(grid[j+1, num+1])
                            ax.imshow(img)
                        # plt.imshow(img)
                        plt.xticks([])
                        plt.yticks([])
                    # print(num, i)
                    ax = plt.subplot(grid[0, num+1])
                    ax.spines['right'].set_visible(False)
                    ax.spines['left'].set_visible(False)
                    ax.spines['top'].set_visible(False)
                    ax.spines['bottom'].set_visible(False)
                    plt.xticks([])
                    plt.yticks([])
                    if isinstance(i, (type(torch.nn.ReLU()),type(Reshape()),type(torch.nn.Softmax()))):
                        act_layer += 0.1
                        ax.text(0.5,0,tra_layer-1+act_layer , ha='center', va='center')
                        str_l += str(tra_layer-1+act_layer)+": "+str(i) + '\n'
                    else: # 传统网络层
                        act_layer = 0
                        ax.text(0.5,0,tra_layer, ha='center', va='center')
                        str_l += str(tra_layer)+": "+str(i) + '\n'
                        tra_layer +=1
                    # print(act_layer)
                ax = plt.subplot(grid[-1, 0])
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['top'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                plt.xticks([])
                plt.yticks([])
                # for i, layer in enumerate(self.model):
                #     str_l += str(i+1)+": "+str(layer) + '\n'
                ax.text(0,0,str_l)

                plt.savefig("{}/{}.jpg".format(dir_name, "total"))

                plt.show()

            print("Visualization result has been saved in {} !".format(dir_name))

    def extract_feature(self,data=None, pretrain=None):
        if len(data.shape) == 2:
            h,w = data.shape
            c = 1
        elif  len(data.shape) == 3:
            h,w,c = data.shape
        data = np.reshape(data, (1,c,h,w))
        data = Variable(torch.tensor(np.array(data)).to(torch.float32))
        if pretrain == None:
            self.model.eval()
            out = self.model(data)
        # elif pretrain == 'resnet34':
        else:
            from torchvision import models,transforms
            transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.CenterCrop(512),
                transforms.Resize(224),
                transforms.ToTensor()
            ])
            if len(data.shape) > 2 and data.shape[0] == 1:
                data = np.squeeze(data)
            data = transform(data)
            c,h,w = data.shape
            data = np.reshape(data, (1, c, h,w))
            # model = models.resnet34(pretrained=True)
            str = "models.{}(pretrained=True)".format(pretrain)
            model = eval(str)
            model.classifier = torch.nn.Sequential()
            model.eval()
            with torch.no_grad():
                out = model(data)
        out = out.detach().numpy()
        return out

    def show_one_layer(self, data, layer_name, num, dir_name):
        if len(data.shape) > 2 and data.shape[0] == 1:
            data = np.squeeze(data)

        for i in range(data.shape[0]):
            img = data[i].detach().numpy()
            if len(img.shape) == 1:
                img = np.reshape(img, (1, img.shape[0]))
            # w, c = img.shape
            # print(w, c)
            # img = np.reshape(img, (w, c))
            plt.subplot(1,data.shape[0], i+1)
            plt.imshow(img)
            plt.xticks([])
            plt.yticks([])

        plt.suptitle(layer_name)
        plt.savefig("{}/{}.jpg".format(dir_name, num))
        # plt.show()

    def load_img_data(self, data_path, classes=None, batch_size=32,train_val_ratio=1.0, shuffle=True,batch_mode=False,transform=None,color="RGB",**kw ):
        from .load_data import ImageFolderDataset
        dataset = ImageFolderDataset(data_path, transform=transform,color=color, batch_mode=batch_mode)
        self.dataset_size = int(len(dataset))
        self.color = color
        self.img_classes = classes
        self.transform = transform
        if 0 < train_val_ratio < 1:
            train_size =  int(train_val_ratio * self.dataset_size)
            val_size =  self.dataset_size - train_size

            train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
            self.dataloader = DataLoader(train_dataset,batch_size=batch_size, shuffle=shuffle,num_workers=1)
            self.val_dataloader = DataLoader(val_dataset,batch_size=batch_size, shuffle=shuffle,num_workers=1)
        else:
            self.dataloader = DataLoader(dataset,batch_size=batch_size, shuffle=shuffle,num_workers=1)

        return self.dataloader

    def load_tab_data(self, data_path,batch_size=32, train_val_ratio=1.0, shuffle=True):
        from .load_data import TabularDataset
        dataset = TabularDataset(data_path)
        self.dataset_size = int(len(dataset))
        # print(self.dataset_size)
        # self.dataloader = DataLoader(dataset,batch_size=batch_size, shuffle=shuffle,num_workers=1)
        if 0 < train_val_ratio < 1:
            train_size =  int(train_val_ratio * self.dataset_size)
            val_size =  self.dataset_size - train_size

            train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
            self.dataloader = DataLoader(train_dataset,batch_size=batch_size, shuffle=shuffle,num_workers=1)
            self.val_dataloader = DataLoader(val_dataset,batch_size=batch_size, shuffle=shuffle,num_workers=1)
        else:
            self.dataloader = DataLoader(dataset,batch_size=batch_size, shuffle=shuffle,num_workers=1)

        return self.dataloader

    def load_npz_data(self, data_path, batch_size=32, shuffle=True, classes=None,train_val_ratio=1.0):
        from .load_data import NpzDataset
        dataset = NpzDataset(data_path)
        self.dataset_size = int(len(dataset))
        self.img_classes = classes

        # print(self.dataset_size)
        self.dataloader = DataLoader(dataset,batch_size=batch_size, shuffle=shuffle,num_workers=1)
        if 0 < train_val_ratio < 1:
            train_size =  int(train_val_ratio * self.dataset_size)
            val_size =  self.dataset_size - train_size

            train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
            self.dataloader = DataLoader(train_dataset,batch_size=batch_size, shuffle=shuffle,num_workers=1)
            self.val_dataloader = DataLoader(val_dataset,batch_size=batch_size, shuffle=shuffle,num_workers=1)
        else:
            self.dataloader = DataLoader(dataset,batch_size=batch_size, shuffle=shuffle,num_workers=1)
        return self.dataloader

    # def load_dataset(self, data_path, batch_size=32,shuffle=True,batch_mode=False,label_column=-1,transform=None,color="RGB",**kw ):
        # from .load_data import ImageFolderDataset
        # from torch.utils.data import DataLoader

        # if data_type == 'tabular':
        #     dataset = ""
        # elif data_type =="image_folder":
        #     dataset = ImageFolderDataset(data_path, transform=transform,color=color, batch_mode=batch_mode)
        # elif data_type == "custom":
        #     dataset = ""
        # else:
        #     raise ValueError(f"Unsupported data_type: {data_type}")
        # self.dataset_size = len(dataset)
        # self.dataloader = DataLoader(dataset,batch_size=batch_size, shuffle=shuffle,num_workers=1)
        # return self.dataloader

    def load_dataset(self, x, y, **kw):
        if kw:
            if 'word2idx'  in kw:
                print("载入词表")
                self.word2idx = kw['word2idx']
                self.idx2word = {v:k for k, v in self.word2idx.items()}
                self.x = torch.from_numpy(x)
                self.y = torch.from_numpy(y)
            if 'classes' in kw:
                # print(kw['classes'])
                if isinstance(kw['classes'],dict):
                    if isinstance(list(kw['classes'].keys())[0],str): # 字典的键为类别，即classes2idx
                        self.img_classes = list(kw['classes'].keys())
                    else: # 字典的值为类别，即idx2classes
                        self.img_classes = list(kw['classes'].values())

                else:
                    self.img_classes = kw['classes']

                self.x = Variable(torch.tensor(np.array(x)).to(torch.float32))
                self.y = Variable(torch.tensor(np.array(y)).long())
        else:
            # self.x = Variable(torch.tensor(np.array(x)).to(torch.float32))
            self.x = torch.from_numpy(x).to(torch.float32)
            # self.y = Variable(torch.tensor(np.array(y)).long())
            self.y = torch.from_numpy(y)

            self.batchsize = self.x.shape[0]
        
        import torch.utils.data as Data
        from torch.utils.data import DataLoader
        dataset = Data.TensorDataset(self.x, self.y)
        self.dataset_size = int(len(dataset))

        self.dataloader = Data.DataLoader(dataset,
                    batch_size = len(dataset),
                    shuffle = True,
                    num_workers = 1)

    def set_seed(self, seed):# 设置随机数种子
        import random
        torch.manual_seed(seed)   #CPU
        torch.cuda.manual_seed(seed)      # 为当前GPU设置随机种子（只用一块GPU）
        torch.cuda.manual_seed_all(seed) # 所有GPU
        np.random.seed(seed)
        random.seed(seed)
        torch.backends.cudnn.deterministic = True
        os.environ['PYTHONHASHSEED'] = str(seed)  # 为了禁止hash随机化，使得实验可复现。

    def train(self, lr=0.1, epochs=30, batch_num=1, batch_size=16, save_fold=None, loss="CrossEntropyLoss" ,metrics=["acc"],filename="basenn.pth", checkpoint=None):
        if self.rnn: # 针对文本任务
            import torch.utils.data as Data
            # from torch.utils.data import DataLoader
            # dataset = Data.TensorDataset(self.x, self.y)
            # self.dataloader = Data.DataLoader(dataset,
            #             batch_size = batch_size,
            #             shuffle = True,
            #             num_workers = 1)
            if checkpoint and self.device== torch.device('cpu'):
                self.model.load_state_dict(torch.load(checkpoint,map_location=torch.device('cpu')))
            elif checkpoint:
                self.model.load_state_dict(torch.load(checkpoint)['state_dict'])
                        
            self.model.to(self.device)

            # 设置优化器
            optimizer = torch.optim.Adam(self.model.parameters(), lr = lr)
            # scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=150, eta_min=0)
            scheduler = torch.optim.lr_sheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=10,verbose=False, threshold=0.0001, threshold_mode='rel', cooldown=0, min_lr=0, eps=1e-08)
            # 设置损失函数
            criterion = torch.nn.CrossEntropyLoss()

            # 定义训练过程
            for epoch in range(epochs):
                for batch_idx, (batch_x, batch_y) in enumerate(self.dataloader,0):

                    batch_x = batch_x.long().transpose(1, 0).contiguous()
                    batch_y = batch_y.long().transpose(1, 0).contiguous()

                    batch_x = batch_x.to(self.device)
                    batch_y = batch_y.to(self.device)
                    output, _ = self.model(batch_x)
                    loss = criterion(output, batch_y.view(-1))

                    if batch_idx % 900 == 0:
                        print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                            epoch+1, batch_idx * len(batch_x[1]), len(self.dataloader.dataset),
                            100. * batch_idx / len(self.dataloader), loss.item()))

                    optimizer.zero_grad()
                    loss.backward()
                    optimizer.step()
                    scheduler.step()

            # 保存模型
            print("保存模型中...")

            info = {
                'meta':{
                    'tool':'BaseNN', 
                    'backbone':self.model, 
                    'device':self.device,
                    'dataset_size':self.dataset_size,
                    'learning_rate':lr,
                    'epoch':epochs,
                    'time': time.asctime( time.localtime(time.time()) ),
                    'word2idx': self.word2idx,

                },
                'state_dict':self.model.state_dict(),
                'para':{
                    'config':self.config,
                    'rnn':self.rnn,
                }

            }
            if save_fold is not None:
                self.save_fold = save_fold
            if self.save_fold is not None:
                if not os.path.exists(self.save_fold):
                    os.mkdir(self.save_fold)
                model_path = os.path.join(self.save_fold, filename)
                torch.save(info, model_path)
                print("保存模型{}成功！".format(model_path))
            else:
                torch.save(info, filename)
                print("保存模型{}成功！".format(filename))

        else: # 针对图像任务
            if checkpoint:
                if not os.path.exists(checkpoint):
                    print("未找到{}文件！".format(checkpoint))
                    return 
                self.model = torch.load(checkpoint)['state_dict']
            # import torch.utils.data as Data
            # dataset = Data.TensorDataset(self.x, self.y)
            # total = self.x.shape[0]
            # self.loader = Data.DataLoader(
            #     dataset=dataset,
            #     batch_size=int(total / batch_num),
            #     shuffle=True,
            #     num_workers=1, # 多线程读数据
            # )
            self.loader = self.dataloader
            loss_str = "torch.nn.{}()".format(loss)
            loss_fun = eval(loss_str)
            print("损失函数：", loss_fun)

            if self.optimizer == 'SGD':
                optimizer = torch.optim.SGD(self.model.parameters(), lr=lr,momentum=0.9)  # 使用SGD优化器
            elif self.optimizer == 'Adam':
                optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
            elif self.optimizer == 'Adagrad':
                optimizer = torch.optim.Adagrad(self.model.parameters(), lr=lr)
            elif self.optimizer == 'ASGD':
                optimizer = torch.optim.ASGD(self.model.parameters(), lr=lr)  
            print("使用 {} 优化器。".format(self.optimizer))
            # scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=10,verbose=False, threshold=0.0001, threshold_mode='rel', cooldown=0, min_lr=0, eps=1e-08)
            self.model.to(self.device)
            log = []
            for epoch in range(epochs):  
                # b_loss = 0
                # b_acc = 0
                for batch_x, batch_y in self.loader:
                    # print("iter ", iter, np.squeeze(batch_x[0]).shape, batch_y[0])
                    # import cv2
                    # cv2.imshow("asd", np.array(np.squeeze(batch_x[0])))
                    # print("batch_y[0]",np.squeeze(batch_y[0]))
                    # y_pred = self.model(self.x)
                    batch_x = batch_x.to(self.device)
                    batch_y = batch_y.to(self.device)

                    optimizer.zero_grad()  # 将梯度初始化为零，即清空过往梯度
                    # print(batch_x.shape,type(batch_x))
                    y_pred = self.model(batch_x)
                    # print(batch_y[0],y_pred[0])
                    # cv2.waitKey(0)

                    loss = loss_fun(y_pred, batch_y)
                    loss.backward()  # 反向传播，计算当前梯度
                    optimizer.step()  # 根据梯度更新网络参数\
                    # scheduler.step()
                    log_info = "{epoch:%d  Loss:%.4f}" % (epoch, loss)
                    log_dict = {"epoch":epoch, "loss":loss.item()}
                    if "acc" in metrics:
                        acc = cal_accuracy(batch_y, y_pred)
                        log_info = log_info[:-1] # 去掉句末大括号
                        log_info+= "  Accuracy:%.4f}"%acc # 加入acc信息
                        log_dict['acc'] = acc
                    if  "mae" in metrics:
                        mae = torch.nn.L1Loss()
                        mae = mae(y_pred, batch_y)
                        log_info = log_info[:-1] # 去掉句末大括号
                        log_info+= "  MAE:%.4f}"%mae # 加入acc信息
                        log_dict['mae'] = mae
                    if "mse" in metrics:
                        mse = torch.nn.MSELoss()
                        mse = mse(y_pred, batch_y)
                        log_info = log_info[:-1] # 去掉句末大括号
                        log_info+= "  MSE:%.4f}"%mse # 加入acc信息
                        log_dict['mse'] = mse
                    print(log_info)
                    log.append(log_dict)
                    # b_acc += acc
                    # b_loss+= loss
                # step+=1
                # print("{epoch:%d  Loss:%.4f  Accuracy:%.4f}" % (epoch, b_loss/step, b_acc/step),step)

            if save_fold:
                self.save_fold = save_fold
                # print(self.save_fold)
            if not os.path.exists(self.save_fold):
                os.mkdir(self.save_fold)

            model_path = os.path.join(self.save_fold, filename)
            print("保存模型中...")
            info = {
                'meta':{
                    'tool':'BaseNN', 
                    'backbone':self.model, 
                    'device':self.device,
                    'dataset_size':self.dataset_size,
                    'learning_rate':lr,
                    'epoch':epochs,
                    'time': time.asctime( time.localtime(time.time()) ),
                    'color':self.color,
                    'transform':self.transform, 
                },
                'state_dict':self.model,
                'para':{
                    'rnn':self.rnn,
                }

            }
            try:
                info['meta']['CLASSES'] = self.img_classes
            except:
                pass
            torch.save(info,model_path)
            # torch.save([self.img_classes, self.model], model_path)
            print("保存模型{}成功！".format(model_path))
            return log

    def inference(self, data, show=False, checkpoint=None,hidden=None, label=False):
        if checkpoint is not None:
            self.rnn = torch.load(checkpoint)['para']['rnn']
        if self.rnn:
            self.word2idx = torch.load(checkpoint)['meta']['word2idx']
            self.ix2word = {v:k for k, v in self.word2idx.items()}
            config = torch.load(checkpoint)['para']['config']
            self.model =  lstm(len(self.word2idx),config['para']['ed'],config['para']['hd'],config['para']['nl'])
            self.model.eval()
            self.model.to(self.device)
            input = torch.Tensor([self.word2idx[data]]).view(1, 1).long()
            output, hidden = self._inference(data=input,checkpoint=checkpoint,hidden=hidden)
            output = output.data[0].cpu()
            lay = torch.nn.Softmax(dim=0)
            output = lay(output)
            return np.array(output),hidden
        else:
            if isinstance(data,str): # 推理文件路径
                file_type = data.split(".")[-1]
                if file_type == "csv":  # 推理csv
                    if not label: # 无标签
                        x = np.loadtxt(data, dtype=float, delimiter=',',skiprows=1)
                        data  = Variable(torch.tensor(np.array(x)).to(torch.float32)).to(self.device)
                    else: # 有标签
                        x = np.loadtxt(data, dtype=float, delimiter=',',skiprows=1)
                        data = x[:, :-1]
                        data  = Variable(torch.tensor(np.array(data)).to(torch.float32)).to(self.device)
                elif file_type.lower() in ["jpg", "png", "jpeg"]:  # 推理图片
                    # img = cv2.imread(data)
                    color = torch.load(checkpoint)['meta']['color']
                    if color == "grayscale":
                        img = cv2.imread(data,cv2.IMREAD_GRAYSCALE)
                        img = np.expand_dims(img, 2)                 
                    else:
                        img = cv2.imread(data)
                    # img = np.array(Image.open(data))
                    transform = torch.load(checkpoint)['meta']['transform']
                    if transform is not None:
                        img = np.array(transform(Image.fromarray(img)))
                    data = torch.from_numpy(img).unsqueeze(0).permute(0,3,1,2).to(torch.float32).to(self.device) 

                    # if len(img.shape) == 2:
                    #     # 灰度，加两维度（sample，channel）
                    #     data = torch.from_numpy(img).unsqueeze(0).unsqueeze(0).to(torch.float32).to(self.device) 
                    # elif len(img.shape) == 3:
                    #     # 灰度/RGB，加一维度（sample）
                    #     data = torch.from_numpy(img).permute(2,0,1).unsqueeze(0).to(torch.float32).to(self.device) 
                    # else:
                    #     print("传入图像的形状不符合要求：",img.shape)
                    #     return
                elif os.path.isdir(data): # 推理文件夹
                    img_list = []
                    dir_list = os.listdir(data)
                    # print(dir_list)
                    # 将顺序读取的文件保存到该list中
                    for item in dir_list:
                        img_path = os.path.join(data,item)
                        # img = np.array(Image.open(img_path))
                        color = torch.load(checkpoint)['meta']['color']
                        if color == "grayscale":
                            img = cv2.imread(img_path,cv2.IMREAD_GRAYSCALE)
                            img = np.expand_dims(img, 2)                 

                        else:
                            img = cv2.imread(img_path)
                        # if len(img.shape) == 2:
                        #     # 灰度，加1维度（channel）
                        #     img = np.expand_dims(img, 0)                 
                        transform = torch.load(checkpoint)['meta']['transform']
                        if transform is not None:
                            img = np.array(transform(Image.fromarray(img)))
                        img_list.append(img)
                    
                    data = torch.from_numpy(np.array(img_list)).permute(0,3,1,2).to(torch.float32).to(self.device) 
                    # x = np.expand_dims(x, axis=1)

            else:  # 推理numpy数组
                data  = Variable(torch.tensor(np.array(data)).to(torch.float32)).to(self.device)
            # print(data.shape)
            # data  = Variable(torch.tensor(np.array(data)))

            if checkpoint:
                self.model = torch.load(checkpoint)['state_dict']
                try:
                    self.img_classes = torch.load(checkpoint)['meta']['CLASSES']
                except:
                    pass
            self.model.eval()
            with torch.no_grad():
                res = self.model(data)
            res = np.array(res.cpu())
            if show:
                print("推理结果为：",res)
            self. res = res
            return res
    
    def _inference(self, data, show=False, checkpoint=None,hidden=None):
        data = data.to(self.device)

        if checkpoint and self.device== torch.device('cpu'):
            self.model.load_state_dict(torch.load(checkpoint,map_location=torch.device('cpu'))[1])
        elif checkpoint:
            sta = torch.load(checkpoint)['state_dict']
            self.model.load_state_dict(sta)

        output, hidden = self.model(data, hidden)
        return output, hidden
    
    def print_model(self):
        # print('模型共{}层'.format(self.layers_num))
        print(self.model)

    def save(self, model_path='basenn.pkl'):
        print("保存模型中...")
        torch.save(self.model, model_path)
        print("保存模型{}成功！".format(model_path))
    
    def load(self,model_path):
        print("载入模型中...")
        # self.model = torch.load(model_path)
        self.model = torch.load(model_path)['state_dict']

        print("载入模型{}成功！".format(model_path))

    def print_result(self, result=None):
        res_idx = self.res.argmax(axis=1)
        res = {}
        for i,idx in enumerate(res_idx):
            try:
                pred = self.img_classes[idx]
            except:
                pred = idx
            res[i] ={"预测值":pred,"置信度":self.res[i][idx]} 
        print("推理结果为：", res)
        return res
    
