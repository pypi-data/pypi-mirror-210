from BaseNN import nn,pth_info
# import torch
import numpy as np
import cv2
import os

def cal_accuracy(y, pred_y):
    res = pred_y.argmax(axis=1)
    tp = np.array(y)==np.array(res)
    acc = np.sum(tp)/ y.shape[0]
    return acc

def read_data(path):
    data = []
    label = []
    dir_list = os.listdir(path)

    # 将顺序读取的文件保存到该list中
    for item in dir_list:
        tpath = os.path.join(path,item)

        # print(tpath)
        for i in os.listdir(tpath):
            # print(item)
            img = cv2.imread(os.path.join(tpath,i))
            imGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # print(img)
            data.append(imGray)
            label.append(int(item))
    x = np.array(data)
    y = np.array(label)

    x = np.expand_dims(x, axis=1)
    return x, y

def only_infer_demo():
    # 测试数据
    test_path = '../../dataset/iris/iris_test.csv'
    test_x = np.loadtxt(test_path, dtype=float, delimiter=',',skiprows=1,usecols=range(0,4))
    test_y = np.loadtxt(test_path, dtype=int, delimiter=',',skiprows=1,usecols=4)

    model = nn()
    checkpoint = 'iris_ckpt/basenn.pth'
    result = model.inference(data=test_x, checkpoint=checkpoint)
    model.print_result(result)

def normal_train_demo():
    model = nn()
    # 训练数据
    train_path = '../../dataset/iris/iris_training.csv'
    x = np.loadtxt(train_path, dtype=float, delimiter=',',skiprows=1,usecols=range(0,4)) # [120, 4]
    y = np.loadtxt(train_path, dtype=int, delimiter=',',skiprows=1,usecols=4)
    model.add(layer='Linear',size=(4, 10),activation='ReLU') # [120, 10]
    # model.add(layer='Dropouttt')
    model.add(layer='Linear',size=(10, 5), activation='ReLU') # [120, 5]
    # model.add(layer='Dropout', p=0.6)
    model.add(layer='Linear', size=(5, 3), activation='Softmax') # [120, 3]
    model.load_dataset(x, y)
    model.save_fold = 'iris_ckpt'
    model.train(lr=0.01, epochs=100)
    # model.print_model()

def continue_train_demo():
    model = nn()
    # 训练数据
    train_path = '../../dataset/iris/iris_training.csv'
    x = np.loadtxt(train_path, dtype=float, delimiter=',',skiprows=1,usecols=range(0,4)) # [120, 4]
    y = np.loadtxt(train_path, dtype=int, delimiter=',',skiprows=1,usecols=4)
    model.load_dataset(x, y)
    model.save_fold = 'checkpoints'
    checkpoint = 'iris_ckpt/basenn.pth'
    model.train(lr=0.01, epochs=10, checkpoint=checkpoint)

def iris_train_test():
    # 训练数据
    train_path = '../../dataset/iris/iris_training.csv'
    x = np.loadtxt(train_path, dtype=float, delimiter=',',skiprows=1,usecols=range(0,4)) # [120, 4]
    y = np.loadtxt(train_path, dtype=int, delimiter=',',skiprows=1,usecols=4)
    # 测试数据
    test_path = '../../dataset/iris/iris_test.csv'
    test_x = np.loadtxt(test_path, dtype=float, delimiter=',',skiprows=1,usecols=range(0,4))
    test_y = np.loadtxt(test_path, dtype=int, delimiter=',',skiprows=1,usecols=4)
    # 声明模型
    model = nn()
    model.add(layer='Linear',size=(4, 10),activation='ReLU') # [120, 10]
    model.add(layer='Linear',size=(10, 5), activation='ReLU') # [120, 5]
    model.add(layer='Linear', size=(5, 3), activation='Softmax') # [120, 3]
    model.load_dataset(x, y)
    # model.print_model()
    model.train(lr=0.01, epochs=5, save_fold='iris_ckpt')
    res = model.inference(test_x)
    model.print_result() # 输出字典格式结果
    # 计算分类正确率
    print("分类正确率为：",cal_accuracy(test_y, res))

def mnist_train():
    # 读取数据
    train_x, train_y = read_data("../../dataset/cls/mnist/training_set")
    model = nn() #声明模型 
    classes = {0:"0",1:"1",2:"2", 3:"3", 4:"4",5:"5",6:"6",7:"7",8:"8",9:"9"}
    model.load_dataset(train_x, train_y,classes=classes) # 载入数据
    # model.set_seed(123465)

    model.add('Conv2D', size=(1, 6),kernel_size=( 5, 5), activation='ReLU') # 60000 * 3456(6 * 24 * 24)
    model.add('AvgPool', kernel_size=(2,2)) # 60000 * 864(6 * 12 * 12)
    model.add('Conv2D', size=(6, 16), kernel_size=(5, 5), activation='ReLU') # 60000 * 1024(16 * 8 * 8)
    model.add('AvgPool', kernel_size=(2,2)) # 60000 * 256(16 * 4 * 4)
    model.add('Linear', size=(256, 120), activation='ReLU')  # 60000 * 256
    model.add('Linear', size=(120, 84), activation='ReLU') 
    model.add('Linear', size=(84, 10), activation='Softmax')

    model.add(optimizer='SGD')

    model.save_fold = 'mn_ckpt'
    # checkpoint = 'mn_ckpt/basenn.pkl'
    # model.train(lr=0.01, epochs=500) # 继续训练
    model.train(lr=0.01, epochs=20,batch_num=1) # 直接训练
    # model.train(lr=0.1, epochs=500) # 直接训练

def mnist_test(one_img):
    # one_img: 布尔值，True时推理一张图片，返回推理结果字典；False时推理整个验证集，返回准确率
    # 读取数据
    test_x, test_y = read_data("../../dataset/cls/mnist/val_set")
    # 模型
    model = nn() # 声明模型
    checkpoint = 'mn_ckpt/basenn.pth' # 载入模型
    if one_img== False:     # 推理整个验证集
        result = model.inference(data=test_x, checkpoint=checkpoint)
        print(result)
        # model.print_result(result)
        acc = cal_accuracy(test_y, result)  # 计算准确率
        print(acc)
        # 训练集准确率：0.9896
        # 验证集准确率：0.9901
    else: # 推理一张图片
        result = model.inference(data=[test_x[0]], checkpoint=checkpoint)
        model.print_result(result)
    

def infer_9_demo():
    model = nn() # 声明模型
    img = cv2.imread("../../111.png",cv2.IMREAD_GRAYSCALE) # 读入测试图片（灰度）
    x = np.expand_dims(img, axis=0) # 增加通道维度
    x = np.expand_dims(x, axis=1) # 增加样本数维度
    # 此时x为四维数组，即[样本数， 通道数，宽， 高]，[1,1,28,28]
    checkpoint = 'mn_ckpt/basenn.pkl'  # 前面训练出的权重文件的路径
    result = model.inference(data=x, checkpoint=checkpoint) # 对该张图片进行推理
    model.print_result(result) # 输出结果

def visual_feature_demo():
    # 读取数据
    train_x, train_y = read_data("../../dataset/cls/mnist/training_set")
    model = nn() #声明模型 
    model.load_dataset(train_x, train_y) # 载入数据
    model.add('Conv2D', size=(1, 6),kernel_size=( 5, 5), activation='ReLU') # 60000 * 3456(6 * 24 * 24)
    model.add('AvgPool', kernel_size=(2,2)) # 60000 * 864(6 * 12 * 12)
    model.add('Conv2D', size=(6, 16), kernel_size=(5, 5), activation='ReLU') # 60000 * 1024(16 * 8 * 8)
    model.add('AvgPool', kernel_size=(2,2)) # 60000 * 256(16 * 4 * 4)
    model.add('Linear', size=(256, 120), activation='ReLU')  # 60000 * 256
    model.add('Linear', size=(120, 84), activation='ReLU') 
    model.add('Linear', size=(84, 10), activation='Softmax')
    model.add(optimizer='SGD')
    model.save_fold = 'mn_ckpt'
    checkpoint = 'mn_ckpt/basenn.pth'
    # model.train(lr=0.1, epochs=30, checkpoint=checkpoint) # 继续训练
    # model.train(lr=0.1, epochs=1) # 直接训练

    img = cv2.imread("/home/user/桌面/pip测试7/dataset/cls/mnist/test_set/0/0.png", cv2.IMREAD_GRAYSCALE)

    model.visual_feature(img, in1img=True)

def extract_feature_demo():
    img = cv2.imread("/home/user/桌面/pip测试7/dataset/cls/mnist/test_set/0/0.png")
    model = nn()
    f1 = model.extract_feature(img, pretrain='resnet34')
    print(f1.shape, f1)
    return f1

def lstm_train_demo():
    # 读取数据
    datas = np.load('tang.npz',allow_pickle=True)
    data = datas['data'] 
    # print("第一条数据：",data[0]) # 观察第一条数据
    word2ix = datas['word2ix'].item() # 汉字对应的索引
    # print("词表:",word2ix) 
    ix2word = datas['ix2word'].item() # 索引对应的汉字
    x, y = data[:200,:-1], data[:200, 1:]

    model = nn()
    model.load_dataset(x, y, word2idx=word2ix) # 载入数据

    model.add('LSTM', size=(128,256),num_layers=2) 
    model.save_fold = '111ckpt'
    model.train(lr=0.005, epochs=1,batch_size=16,checkpoint='model_lstm.pth')

def lstm_infer_demo():
    from BaseNN import nn
    model = nn()

    input = '长'
    checkpoint = 'model_lstm.pth'
    output, hidden = model.inference(data=input,checkpoint=checkpoint) # output是多维向量，接下来转化为汉字
    print("output: ",output)
    index = np.argmax(output) # 找到概率最大的字的索引
    w = model.ix2word[index] # 根据索引从词表中找到字
    print("word:",w)

import torch 
class LSTM_model(torch.nn.Module):
    def __init__(self, actions):
        super(LSTM_model, self).__init__()

        self.actions = actions

        self.lstm1 = torch.nn.LSTM(132, 128, batch_first=True, bidirectional=False)
        self.dropout1 = torch.nn.Dropout(0.2)
        self.lstm2 = torch.nn.LSTM(128, 256, batch_first=True, bidirectional=False)
        self.dropout2 = torch.nn.Dropout(0.2)
        self.lstm3 = torch.nn.LSTM(256, 256, batch_first=True, bidirectional=False)
        self.bn = torch.nn.BatchNorm1d(256)
        self.dense1 = torch.nn.Linear(256, 256)
        self.dense2 = torch.nn.Linear(256, 128)
        self.dense3 = torch.nn.Linear(128, 64)
        self.dense4 = torch.nn.Linear(64, actions.shape[0])
        self.softmax = torch.nn.Softmax(dim=1)

    def forward(self, x):
        x, _ = self.lstm1(x)
        x = self.dropout1(x)
        x, _ = self.lstm2(x)
        x = self.dropout2(x)
        x, _ = self.lstm3(x[:, -1, :].unsqueeze(1))
        x = self.bn(x.squeeze())
        x = self.dense1(x)
        x = self.dense2(x)
        x = self.dense3(x)
        x = self.dense4(x)
        x = self.softmax(x)

        return x
def user_defined_demo():
    from BaseNN import nn as bnn
    # 读取数据
    X = np.load("/home/user/桌面/BaseNN004/BaseNN/examples/human_action_recognition-main/X1.npy",allow_pickle = True)
    y = np.load("/home/user/桌面/BaseNN004/BaseNN/examples/human_action_recognition-main/y1.npy", allow_pickle = True)    
    print(y.shape)
    train_x,train_y = X,y.astype(np.float32)
    # 自定义一个mylstm模型
    actions = np.array(["walking","boxing","handwaving"])
    mylstm = LSTM_model(actions)
    # 声明模型
    model = bnn()
    model.load_dataset(train_x, train_y)
    model.add(mylstm)
    model.save_fold = "action_ud"
    # model.train(lr=0.01, epochs=200,loss="BCELoss",metrics=[])

class MyUnsqueeze(torch.nn.Module):
    def __init__(self, *args):
        super(MyUnsqueeze, self).__init__()

    def forward(self, x):
        # print("unsqueeze",type(x), type(x[:, -1, :].unsqueeze(1)))
        return x[:, -1, :].unsqueeze(1)
    
class MySqueeze(torch.nn.Module):
    def __init__(self, *args):
        super(MySqueeze, self).__init__()

    def forward(self, x):
        return x.squeeze()

def data_define_demo():
    # 读取数据
    X = np.load("/home/user/桌面/BaseNN004/BaseNN/examples/human_action_recognition-main/X1.npy",allow_pickle = True)
    y = np.load("/home/user/桌面/BaseNN004/BaseNN/examples/human_action_recognition-main/y1.npy", allow_pickle = True)    

    train_x,train_y = X,y.astype(np.float32)
    test_x, test_y = X[28:38,:,:], y[28:38,:].astype(np.float32)
    # print(X.shape,train_x.shape, train_y.shape)
    # 搭建模型
    model = nn()
    model.load_dataset(train_x, train_y)
    model.add('lstm', size=(132,128))
    model.add('Dropout',p=0.2)
    model.add('lstm', size=(128,256))
    model.add('Dropout',p=0.2)
    model.add(MyUnsqueeze())
    model.add('lstm', size=(256,256))
    model.add(MySqueeze())
    model.add('BatchNorm1d', size=256)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    model.add('Linear',  size=(256, 256))
    model.add('Linear',  size=(256, 128))
    model.add('linear',  size=(128, 64))
    model.add('Linear',  size=(64, 3))
    model.add(activation='Softmax')
    model.save_fold = "action_ckpt1"
    log = model.train(lr=0.01, epochs=200,loss="BCELoss",metrics=[])
    print(log)

def action_demo():
    # 读取数据
    X = np.load("/home/user/桌面/BaseNN004/BaseNN/examples/human_action_recognition-main/X1.npy",allow_pickle = True)
    y = np.load("/home/user/桌面/BaseNN004/BaseNN/examples/human_action_recognition-main/y1.npy", allow_pickle = True)    

    train_x,train_y = X,y.astype(np.float32)
    test_x, test_y = X[28:38,:,:], y[28:38,:].astype(np.float32)
    # print(X.shape,train_x.shape, train_y.shape)
    # 搭建模型
    model = nn()
    model.load_dataset(train_x, train_y)
    model.add('lstm', size=(132,128))
    model.add('Dropout',p=0.2)
    model.add('lstm', size=(128,256))
    model.add('Dropout',p=0.2)
    model.add('unsqueeze')
    model.add('lstm', size=(256,256))
    model.add('squeeze')
    model.add('BatchNorm1d', size=256)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    model.add('Linear',  size=(256, 256))
    model.add('Linear',  size=(256, 128))
    model.add('linear',  size=(128, 64))
    model.add('Linear',  size=(64, 3))
    model.add(activation='Softmax')
    model.save_fold = "action_ckpt1"
    # model.train(lr=0.01, epochs=200,loss="BCELoss",metrics=[])

    res = model.inference(test_x, checkpoint="action_ckpt1/basenn.pth")
    print(test_y)
    print(res)

def load_image_data_mn():

    model = nn()
    # model.set_seed(123465)

    # model.load_img_data("/home/user/桌面/BaseNN004/dataset/cls/mnist/training_set",
    #                          data_type='image_folder',color="grayscale",batch_size=60000)

    # model.add('Conv2D', size=(1, 6),kernel_size=( 5, 5), activation='ReLU') # 60000 * 3456(6 * 24 * 24)
    # model.add('AvgPool', kernel_size=(2,2)) # 60000 * 864(6 * 12 * 12)
    # model.add('Conv2D', size=(6, 16), kernel_size=(5, 5), activation='ReLU') # 60000 * 1024(16 * 8 * 8)
    # model.add('AvgPool', kernel_size=(2,2)) # 60000 * 256(16 * 4 * 4)
    # model.add('Linear', size=(256, 120), activation='ReLU')  # 60000 * 256
    # model.add('Linear', size=(120, 84), activation='ReLU') 
    # model.add('Linear', size=(84, 10), activation='Softmax')
    # model.add(optimizer='SGD')
    # model.save_fold = 'new_mn_ckpt'
    # model.train(lr=0.01, epochs=20, checkpoint="new_mn_ckpt/basenn.pth") # 直接训练
    test_x, y = read_data("../../dataset/cls/mnist/val_set")
    print(y[1000:1100])
    a = "../../dataset/cls/mnist/val_set/4/85.png"
    b = "../../dataset/cls/mnist/val_set/4"
    result = model.inference(data=a, checkpoint="new_mn_ckpt/basenn.pth")
    model.print_result()

def load_image_data_cd():
    from torchvision.transforms import transforms
    model = nn()
    # model.set_seed(123465)
    tran = transforms.Resize([128,128])
    classes = {0:"cat", 1:"dog"}
    d = model.load_img_data("/home/user/桌面/BaseNN004/dataset/cls/cats_dogs_dataset/CatsDogs (1)/CatsDogs/training_set",
                             color="RGB",batch_size=1000, transform=tran,classes=classes)
    # # for x, y in d:
    # #     print(x.shape)
    model.add('Conv2D', size=(3, 6),kernel_size=( 5, 5), activation='ReLU') # 60000 * 3456(6 * 24 * 24)
    model.add('AvgPool', kernel_size=(2,2)) # 60000 * 864(6 * 12 * 12)
    model.add('Conv2D', size=(6, 16), kernel_size=(5, 5), activation='ReLU') # 60000 * 1024(16 * 8 * 8)
    model.add('AvgPool', kernel_size=(2,2)) # 60000 * 256(16 * 4 * 4)
    model.add('Linear', size=(13456, 120), activation='ReLU')  # 60000 * 256
    model.add('Linear', size=(120, 84), activation='ReLU') 
    model.add('Linear', size=(84, 10), activation='Softmax')
    model.add(optimizer='SGD')
    model.save_fold = 'new_cd_ckpt'
    model.train(lr=0.01, epochs=10) # 直接训练
    # test_x, y = read_data("../../dataset/cls/mnist/val_set")
    # print(y[1000:1100])
    a = "/home/user/桌面/BaseNN004/dataset/cls/cats_dogs_dataset/CatsDogs (1)/CatsDogs/val_set/dog"
    b = "/home/user/桌面/BaseNN004/dataset/cls/cats_dogs_dataset/CatsDogs (1)/CatsDogs/val_set/dog/dog0.jpg"
    result = model.inference(data=b, checkpoint="new_cd_ckpt/basenn.pth")
    model.print_result()

def load_tab_data_iris():
    model = nn()
    # 训练数据
    train_path = '../../dataset/iris/iris_training.csv'
    # x = np.loadtxt(train_path, dtype=float, delimiter=',',skiprows=1,usecols=range(0,4)) # [120, 4]
    # y = np.loadtxt(train_path, dtype=int, delimiter=',',skiprows=1,usecols=4)
    train,val = model.load_tab_data(train_path, batch_size=2,train_val_ratio=0.8)
    # for x, y in dl:
    #     print(x,y)

    # model.add(layer='Linear',size=(4, 10),activation='ReLU') # [120, 10]
    # model.add(layer='Linear',size=(10, 5), activation='ReLU') # [120, 5]
    # model.add(layer='Linear', size=(5, 3), activation='Softmax') # [120, 3]
    # model.save_fold = 'iris_ckpt'
    # model.train(lr=0.01, epochs=500)
    # model.print_model()
    # test_path = '../../dataset/iris/iris_test.csv'
    # x = np.loadtxt(test_path, dtype=float, delimiter=',',skiprows=1,usecols=range(0,4)) # [120, 4]
    # y = np.loadtxt(test_path, dtype=int, delimiter=',',skiprows=1,usecols=4)
    # print(y)
    res = model.inference(val,label=True, checkpoint="iris_ckpt/basenn.pth")
    model.print_result(res)
    print(model.val_label)

def load_npz_data_action():
    # 读取数据
    X = np.load("/home/user/桌面/BaseNN004/BaseNN/examples/human_action_recognition-main/X1.npy",allow_pickle = True)
    y = np.load("/home/user/桌面/BaseNN004/BaseNN/examples/human_action_recognition-main/y1.npy", allow_pickle = True)    
    X = np.load("./conbined.npz")["data"]

    # print(X.shape)
    # np.savez("conbined.npz", data=X, label=y)
    # a = np.load("conbined.npz")
    # print(a['label'].shape)
    # train_x,train_y = X,y.astype(np.float32)
    test_x, test_y = X[28:38,:,:], y[28:38,:].astype(np.float32)
    # # print(X.shape,train_x.shape, train_y.shape)
    # # 搭建模型
    model = nn()
    model.load_npz_data("./conbined.npz",batch_size=50,classes=["a", "b", "c"])
    model.add('lstm', size=(132,128))
    model.add('Dropout',p=0.2)
    model.add('lstm', size=(128,256))
    model.add('Dropout',p=0.2)
    model.add('unsqueeze')
    model.add('lstm', size=(256,256))
    model.add('squeeze')
    model.add('BatchNorm1d', size=256)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    model.add('linear',  size=(256, 256))
    model.add('Linear',  size=(256, 128))
    model.add('linear',  size=(128, 64))
    model.add('Linear',  size=(64, 3))
    model.add(activation='Softmax')
    model.save_fold = "action_ckpt2"
    model.train(lr=0.01, epochs=10,loss="BCELoss",metrics=[])

    res = model.inference(test_x, checkpoint="action_ckpt2/basenn.pth")
    print(test_y)
    print(res)
    model.print_result()

if __name__=="__main__":
    # action_demo()
    # user_defined_demo()
    # data_define_demo()
    # normal_train_demo()
    # pth_info('iris_ckpt/basenn.pth')
    # only_infer_demo()
    # continue_train_demo()
    # iris_train_test()

    # mnist_train()
    # pth_info('mn_ckpt/basenn.pth')
    # mnist_test(True)

    # infer_9_demo()
    # visual_feature_demo()
    # extract_feature_demo()

    # lstm_train_demo()
    # pth_info('model_lstm.pth')
    # lstm_infer_demo()

    # load_image_data_mn()
    # load_image_data_cd()
    load_tab_data_iris()
    # load_npz_data_action()
