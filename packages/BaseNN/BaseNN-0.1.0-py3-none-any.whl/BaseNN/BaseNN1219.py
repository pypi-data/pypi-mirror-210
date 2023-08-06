import os
import torch
import torch.nn 
from torch.autograd import Variable
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')


class Reshape(torch.nn.Module):
    def __init__(self, *args):
        super(Reshape, self).__init__()
        self.shape = args

    def forward(self, x):
        # print(x.shape,x.view(x.shape[0], -1).shape)
        return x.view(x.shape[0], -1)

def cal_accuracy(y, pred_y):
    res = pred_y.argmax(axis=1)
    tp = np.array(y)==np.array(res)
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
        if save_fold != None:
            self.save_fold = save_fold
 

    def add(self, layer=None, activation=None, optimizer=None, **kw):
        self.layers_num += 1
        self.layers.append(layer)
        if layer == 'Linear':
            self.model.add_module('Reshape', Reshape(self.batchsize))
            self.model.add_module('Linear' + str(self.layers_num), torch.nn.Linear(kw['size'][0], kw['size'][1]))
            print("增加全连接层，输入维度:{},输出维度：{}。".format(kw['size'][0], kw['size'][1]))
        elif layer == 'Reshape':
            self.model.add_module('Reshape', Reshape(self.batchsize))
        # elif layer == 'ReLU':
        #     self.model.add_module('ReLU' + str(self.layers_num), nn.ReLU())
        #     print("增加ReLU层。")
        elif layer == 'Conv2D':
            self.model.add_module('Conv2D' + str(self.layers_num), torch.nn.Conv2d(kw['size'][0], kw['size'][1], kw['kernel_size']))
            print("增加卷积层，输入维度:{},输出维度：{},kernel_size: {} ".format(kw['size'][0], kw['size'][1], kw['kernel_size']))
        elif layer == 'MaxPool':
            self.model.add_module('MaxPooling' + str(self.layers_num), torch.nn.MaxPool2d(kw['kernel_size']))
            print("增加最大池化层,kernel_size: {} ".format(kw['kernel_size']))
        elif layer == 'AvgPool':
            self.model.add_module('MaxPooling' + str(self.layers_num), torch.nn.AvgPool2d(kw['kernel_size']))
            print("增加平均池化层,kernel_size: {} ".format(kw['kernel_size']))
        elif layer == 'Dropout':
            p = 0.5 if 'p' not in kw.keys() else kw['p']
            self.model.add_module('Dropout' + str(self.layers_num), torch.nn.Dropout(p=p) )
            print("增加Dropout层,参数置零的概率为: {} ".format(p))

    
        # 激活函数
        if activation == 'ReLU':
            self.model.add_module('ReLU' + str(self.layers_num), torch.nn.ReLU())
            print("使用ReLU激活函数。")
        elif activation == 'Softmax':
            self.model.add_module('Softmax'+str(self.layers_num), torch.nn.Softmax())
            print('使用Softmax激活函数。')

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


    def load_dataset(self, x, y):
        self.x = Variable(torch.tensor(np.array(x)).to(torch.float32))
        self.y = Variable(torch.tensor(np.array(y)).long())

        self.batchsize = self.x.shape[0]

    def set_seed(self, seed):# 设置随机数种子
        import random
        torch.manual_seed(seed)   #CPU
        torch.cuda.manual_seed(seed)      # 为当前GPU设置随机种子（只用一块GPU）
        torch.cuda.manual_seed_all(seed) # 所有GPU
        np.random.seed(seed)
        random.seed(seed)
        torch.backends.cudnn.deterministic = True
        os.environ['PYTHONHASHSEED'] = str(seed)  # 为了禁止hash随机化，使得实验可复现。

    def train(self, lr=0.1, epochs=30, batch_num=1, save_fold=None, loss="CrossEntropyLoss" ,metrics=["acc"],filename='basenn.pkl', checkpoint=None):
        if checkpoint:
            if not os.path.exists(checkpoint):
                print("未找到{}文件！".format(checkpoint))
                return 
            self.model = torch.load(checkpoint)
        import torch.utils.data as Data
        dataset = Data.TensorDataset(self.x, self.y)
        total = self.x.shape[0]
        self.loader = Data.DataLoader(
            dataset=dataset,
            batch_size=int(total / batch_num),
            shuffle=True,
            num_workers=0, # 多线程读数据
        )
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
        for epoch in range(epochs):  
            # b_loss = 0
            # b_acc = 0
            for iter, (batch_x, batch_y) in enumerate(self.loader, 0):
                # print("iter ", iter, np.squeeze(batch_x[0]).shape, batch_y[0])
                # import cv2
                # cv2.imshow("asd", np.array(np.squeeze(batch_x[0])))
                # cv2.waitKey(0)
                # print("batch_y[0]",np.squeeze(batch_y[0]))
                # y_pred = self.model(self.x)
                y_pred = self.model(batch_x)
                # print(y_pred, self.y)
                loss = loss_fun(y_pred, batch_y)
                optimizer.zero_grad()  # 将梯度初始化为零，即清空过往梯度
                loss.backward()  # 反向传播，计算当前梯度
                optimizer.step()  # 根据梯度更新网络参数\
                log_info = "{epoch:%d  Loss:%.4f}" % (epoch, loss)
                if "acc" in metrics:
                    acc = cal_accuracy(batch_y, y_pred)
                    log_info = log_info[:-1] # 去掉句末大括号
                    log_info+= "  Accuracy:%.4f}"%acc # 加入acc信息
                if  "mae" in metrics:
                    mae = torch.nn.L1Loss()
                    mae = mae(y_pred, batch_y)
                    log_info = log_info[:-1] # 去掉句末大括号
                    log_info+= "  MAE:%.4f}"%mae # 加入acc信息
                if "mse" in metrics:
                    mse = torch.nn.MSELoss()
                    mse = mse(y_pred, batch_y)
                    log_info = log_info[:-1] # 去掉句末大括号
                    log_info+= "  MSE:%.4f}"%mse # 加入acc信息
                print(log_info)

        if save_fold:
            self.save_fold = save_fold
            # print(self.save_fold)
        if not os.path.exists(self.save_fold):
            os.mkdir(self.save_fold)

        model_path = os.path.join(self.save_fold, filename)
        print("保存模型中...")
        torch.save(self.model, model_path)
        print("保存模型{}成功！".format(model_path))

    def inference(self, data, show=False, checkpoint=None):
        data  = Variable(torch.tensor(np.array(data)).to(torch.float32))
        if checkpoint:
            self.model = torch.load(checkpoint)

        with torch.no_grad():
            res = self.model(data)
        res = np.array(res)
        if show:
            print("推理结果为：",res)
        self. res = res
        return res

    def print_model(self):
        # print('模型共{}层'.format(self.layers_num))
        print(self.model)

    def save(self, model_path='basenn.pkl'):
        print("保存模型中...")
        torch.save(self.model, model_path)
        print("保存模型{}成功！".format(model_path))
    
    def load(self,model_path):
        print("载入模型中...")
        self.model = torch.load(model_path)
        print("载入模型{}成功！".format(model_path))

    def print_result(self, result=None):
        res_idx = self.res.argmax(axis=1)
        res = {}
        for i,idx in enumerate(res_idx):
            res[i] ={"预测值":idx,"置信度":self.res[i][idx]} 
        print("推理结果为：", res)
        return res
