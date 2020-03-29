import cpptext
import struct
import numpy as np
import os
import cv2
import wx
import sys
#编码
'''剪切+定位二维码->解码->生成v.bin文件'''
def decode(filenames,nx,ny,decodePath,voutPath):
    '''
    运用简单的0->黑，1->白的思想
    '''
    picture_num = filenames.__len__()#获取图片个数
    str_binary = ''
    num_binary = 0
    right="0011"
    p_Number=0
    vout_binary = ''
    k=0
    for k in range(picture_num):
        img = cv2.imread(filenames[k],0)#逐个加载图片
        img = cv2.resize(img, (nx, ny), interpolation=cv2.INTER_AREA)
        ret3,bimg = cv2.threshold(img,155,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        
        #判断是不是同一张图片：
        temp=''
        for j in range(0,4):
            if(img[8,j]>=0 and img[8,j]<=120):#是黑色点
                temp=temp+'0'
            elif(img[8,j]>=160 and img[8,j]<=255):
                temp=temp+'1'
        if(temp==right):
            samepicture=0
            if(right=="0011"):
                right="1100"
            elif(right=="1100"):
                right="0011"
        else:samepicture=1
        #开始解码 遍历所有像素
        if(samepicture==0):
            p_Number+=1
            for i in range(ny):
                if(i>=0 and i<=7):
                    for j in range(8,nx-8):
                        if(num_binary==8):
                           str_binary=str_binary+' '
                           vout_binary=vout_binary+' '
                           num_binary=0
                        if(img[i,j]>=0 and img[i,j]<=ret3-20):#是黑色点
                            str_binary=str_binary+'0'
                            num_binary+=1
                            vout_binary +='1'
                        elif(img[i,j]>=ret3+20 and img[i,j]<=255):#白色  
                            str_binary=str_binary+'1'
                            num_binary+=1
                            vout_binary +='1'
                        else:
                            str_binary=str_binary+'1'
                            num_binary+=1
                            vout_binary +='0'
                elif(i==8):
                    for j in range(4,nx):
                        if(num_binary==8):
                           str_binary=str_binary+' '
                           vout_binary=vout_binary+' '
                           num_binary=0
                        if(img[i,j]>=0 and img[i,j]<=ret3-20):#是黑色点
                            str_binary=str_binary+'0'
                            num_binary+=1
                            vout_binary +='1'
                        elif(img[i,j]>=ret3+20 and img[i,j]<=255):#白色
                            str_binary=str_binary+'1'
                            num_binary+=1
                            vout_binary +='1'
                        else:
                            str_binary=str_binary+'1'
                            num_binary+=1
                            vout_binary+='0'
                elif(i>=9 and i<=ny-9):
                    for j in range (nx):
                        if(num_binary==8):
                           str_binary=str_binary+' '
                           vout_binary=vout_binary+' '
                           num_binary=0
                        if(img[i,j]>=0 and img[i,j]<=ret3-20):#是黑色点
                            str_binary=str_binary+'0'
                            num_binary+=1
                            vout_binary +='1'
                        elif(img[i,j]>=ret3+20 and img[i,j]<=255):#白色            
                            str_binary=str_binary+'1'
                            num_binary+=1
                            vout_binary +='1'
                        else:
                            str_binary=str_binary+'1'
                            num_binary+=1
                            vout_binary +='0'
                elif(i>=ny-8 and i<=ny-1):
                    for j in range (8,nx-8):
                        if(num_binary==8):
                           str_binary=str_binary+' '
                           vout_binary=vout_binary+' '
                           num_binary=0
                        if(img[i,j]>=0 and img[i,j]<=ret3-20):#是黑色点
                            str_binary=str_binary+'0'
                            num_binary+=1
                            vout_binary +='1'
                        elif(img[i,j]>=ret3+20 and img[i,j]<=255):#白色           
                            str_binary=str_binary+'1'
                            num_binary+=1
                            vout_binary +='1'
                        else:
                            str_binary=str_binary+'1'
                            num_binary+=1
                            vout_binary +='0'

    array = np.array([int(b,2) for b in str_binary.split(' ')])
    vout_array = np.array([int(b,2) for b in vout_binary.split(' ')])
    alength = len(array)
    with open(decodePath,'wb') as f:
        for i in range(alength):
            f.write(struct.pack('B',array[i]))
    f.close()
    
    vlength = len(vout_array)
    with open(voutPath,'wb') as f:
        for i in range(vlength):
            f.write(struct.pack('B',vout_array[i]))
    f.close()
    return p_Number

#剪切视频
def get_image(newmp4,image_path):
    video_path = newmp4
    frame = 15
    os.system('ffmpeg -i  {0} -r {1} -f image2 {2}\%d.png'.format(video_path, frame, image_path))

class MyFrame(wx.Frame):  # 编写窗口的类
    def __init__(self, parent, id):  # 类的本身属性
        wx.Frame.__init__(self, parent, id, title="图片解码系统", size=(600, 250))
        panel = wx.Panel(self)  # 显示画板
        title = wx.StaticText(panel, label="请在下方填入想要的相关操作", pos=(160, 10))
        font = wx.Font(15, wx.DEFAULT, wx.FONTSTYLE_NORMAL, wx.LIGHT, underline=False)
        title.SetFont(font)
        title.SetForegroundColour("yellow")  # 设置字体的前景色和背景色
        title.SetBackgroundColour("blue")
        self.filename = wx.StaticText(panel, label="选择目标文件夹:", pos=(10, 35))
        self.filename.SetFont(font)
        self.file = wx.TextCtrl(panel, pos=(163, 35), size=(267,26), style=wx.TE_LEFT)
        self.search1 = wx.Button(panel, label="浏览文件夹", pos=(435, 33), size=(85, 27))
        #文件浏览按钮，驱动文件浏览的事件生成
        self.search1.Bind(wx.EVT_BUTTON, self.Onclicksearch1)
        
        self.filename2 = wx.StaticText(panel, label="输入拍摄视频名：", pos=(10, 70))
        self.filename2.SetFont(font)
        self.file2 = wx.TextCtrl(panel, pos=(163, 68), size=(267,26), style=wx.TE_LEFT)
        wx.StaticText(panel,label="示例：1.mp4",pos=(435,70))

        self.video = wx.StaticText(panel,label="输入解码文件名：",pos=(10,103))
        self.video.SetFont(font)
        self.videovalue = wx.TextCtrl(panel,pos=(163,100),size=(267,26),style=wx.TE_LEFT)
        wx.StaticText(panel, label="示例：decode1.bin", pos=(435, 103))
        
        self.voutpath = wx.StaticText(panel, label="选定vout文件名：", pos=(10, 133))
        self.voutpath.SetFont(font)
        self.voutpathvalue = wx.TextCtrl(panel,pos=(163,130),size=(267, 26),style=wx.TE_LEFT)
        wx.StaticText(panel, label="示例：v1.bin", pos=(435, 130))

        clear = wx.Button(panel, label="清除", pos=(110, 165), size=(90, 37))
        clear.Bind(wx.EVT_BUTTON, self.Onclickclear)
        confirm = wx.Button(panel, label="运行", pos=(230, 165), size=(90, 37))
        confirm.Bind(wx.EVT_BUTTON, self.Onclickconfirm)

        cancel = wx.Button(panel, label="退出", pos=(350, 165), size=(90, 37))
        cancel.Bind(wx.EVT_BUTTON, self.Onclickcancel)

    def Onclickcancel(self, event):
        """取消并退出程序"""
        exitdialog = wx.MessageDialog(None,'Are you sure you want to exit the program?','Notice',
                                      wx.YES_NO|wx.ICON_QUESTION)
        ans = exitdialog.ShowModal()
        if(ans == wx.ID_YES):
            sys.exit()
        else:
            exitdialog.Destroy()

    def Onclickclear(self, event):
        """清除所选定的文本值"""
        cleardialog = wx.MessageDialog(None, '确认清除文本？', 'Notice',
                                      wx.YES_NO | wx.ICON_QUESTION)
        ans = cleardialog.ShowModal()
        if (ans == wx.ID_YES):
            self.file.SetValue("")
            self.file2.SetValue("")
            self.videovalue.SetValue("")
            self.picpathvalue.SetValue("")
            self.voutpathvalue.SetValue("")
        cleardialog.Destroy()



    def Onclickconfirm(self, event):
        """主要是为了执行编码程序的，注意:是在已经创建了.bin文件的基础上"""
        try:
            path = self.file.GetValue()  # 基础文件夹路径
            newmp4 = path+'\\'+self.file2.GetValue()
            decodePath = path+'\\'+self.videovalue.GetValue()
            voutPath = path+'\\'+self.voutpathvalue.GetValue()
            # 视频剪切图片
            get_image(newmp4, path)
            # 计算png图片个数,并传递给decode
            filelist = os.listdir(path)
            picture_num = 0  # 统计png个数
            for item in filelist:
                if item.endswith('.png'):
                    picture_num += 1
            images = []  # 用于存储图片信息的string数组
            for i in range(1, picture_num + 1):
                images.append(str(i) + ".png")
            # 视频剪切
            cpptext.getQrcode(picture_num)
            # 解码
            pictureNum = decode(images, 90, 90, decodePath,voutPath)
            wx.MessageBox("成功解码了"+str(pictureNum)+"张图片.\n And 所有文件生成成功.")
        except Exception as e:
            wx.MessageBox("Error:" + str(e) + "\nPlease check if there is something wrong with your input.")

    def Onclicksearch1(self, event):
        """选定存放图片的位置"""
        dlg = wx.DirDialog(self, "选择文件夹", os.getcwd(),style=wx.DD_DEFAULT_STYLE)
        #选定文件，则文件目录显示在第一个TextCtrl中
        if dlg.ShowModal() == wx.ID_OK:
            self.file.SetValue(dlg.GetPath())
            os.chdir(dlg.GetPath())

    def Onclicksearch2(self, event):
        wildcard = "bin文件(.bin)|*.bin"
        # 可以选定生成的文件类型
        dlg = wx.FileDialog(self, "选择之前编码的二进制文件", os.getcwd(), "", wildcard)
        if dlg.ShowModal() == wx.ID_OK:
            self.picpathvalue.SetValue(dlg.GetPath())



if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame(parent=None, id=-1)
    frame.Center()
    frame.Show()
    app.MainLoop()