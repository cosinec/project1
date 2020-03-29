import cv2
import numpy as np
import struct
import random
import wx
import os
import sys

#随机生成 1个 encode.bin
def getencode(encodePath):
    MAX_LENGTH = 2621440 #2.5M=2621440B
    fo = open(encodePath, "wb")
    length = MAX_LENGTH #文件大小2.5M
    if fo.closed:
        print("error")
    else:
        for x in range(length):
            a = random.randint(-128, 127)
            w = struct.pack('b', a)
            fo.write(w)
        fo.close()

# 编码
def encode(nx,ny,filename1,picture_num):
    '''边读文件边存图片'''
    binaryNum = "0011"#图片筛选标志
    with open(filename1,'rb') as file:
        for m in range(picture_num): 
            str1 = file.read(980)
            lenstr1 = len(str1)#长度
            i = 0#str1字符串下标
            strs = ''#用于存储二进制结果。8位二进制
            while lenstr1:
            #print(str1[i])
                if(str1[i]==1 or str1[i]==0):
                    temp = ' '.join([bin(str1[i]).replace('0b', '0000000')])
                elif (str1[i]>=2 and str1[i]<=3):
                    temp = ' '.join([bin(str1[i]).replace('0b', '000000')])
                elif (str1[i]>=4 and str1[i]<=7):
                    temp = ' '.join([bin(str1[i]).replace('0b', '00000')])
                elif (str1[i]>=8 and str1[i]<=15):
                    temp = ' '.join([bin(str1[i]).replace('0b', '0000')])
                elif (str1[i]>=16 and str1[i]<=31):
                    temp = ' '.join([bin(str1[i]).replace('0b', '000')])
                elif(str1[i]>=32 and str1[i]<=63):
                    temp = ' '.join([bin(str1[i]).replace('0b', '00')])
                elif (str1[i]>=64 and str1[i]<=127):
                    temp = ' '.join([bin(str1[i]).replace('0b', '0')])
                elif (str1[i]>=128):
                    temp = ' '.join([bin(str1[i]).replace('0b', '')])
                strs = strs + temp#字符串拼接
                i += 1
                lenstr1 -= 1
        
            #编码开始
            value=0#strs字符串下标
            length = len(strs)#二进制字符串长度
            ##生成一张白色图片，随后对相关的项目进行改动
            Img = np.zeros((nx,ny),dtype = np.uint8)+255
            
            #判断标志
            lenNum = len(binaryNum)
            for k in range(lenNum):
                if(binaryNum[k]=='0'):
                    Img[9][k+1] = 0
                    
            '''绘制定位点'''
            #上面两个定位点
            Img[1][1:8] = 0
            Img[1][nx-8:nx-1] = 0
            for i in range(2, 8):
                Img[i][1] = Img[i][7] = 0
                Img[i][nx-8] = Img[i][nx-2] = 0
                if(i>=3 and i<=5):
                    Img[i][3:6] = 0
                    Img[i][nx-6:nx-3] = 0
            Img[i][1:8] = Img[i][nx-8:nx-1] = 0
            #左下角
            Img[ny-8][nx-8:nx-1] = 0
            Img[ny-8][1:8] = 0
            for i in range(ny-7, ny-1):
                Img[i][1] = Img[i][7] = 0
                Img[i][nx-8] = Img[i][nx-2] = 0
                if(i>=ny-6 and i<=ny-4):
                    Img[i][3:6] = 0
                    Img[i][nx-6:nx-3] = 0
            Img[i][1:8] = Img[i][nx-8:nx-1] = 0
        
            ##改变像素点
            for i in range(1,ny-1):#imax=ny-1
                if length == 0:#判断是否读取完毕
                    break
                if((i>=1 and i<=8) or (i>=ny-9 and i<=ny-2)):
                    for j in range(9, nx-9):
                        if length == 0:#判断是否读取完毕
                            break
                        if strs[value] == '0':
                            Img[i][j] = 0
                        value += 1
                        length -= 1
                elif(i == 9):
                    for j in range(5,nx-1):#跳过判断标志
                        if length == 0:#判断是否读取完毕
                            break
                        if strs[value] == '0':
                            Img[i][j] = 0
                        value += 1
                        length -= 1
                else:
                    for j in range(1,nx-1):
                        if length == 0:#判断是否读取完毕
                            break
                        if strs[value] == '0':
                            Img[i][j] = 0
                        value += 1
                        length -= 1
            Img = cv2.resize(Img, (int(ny*20), int(nx*20)), interpolation=cv2.INTER_NEAREST)
            cv2.imwrite(str(m)+'.jpg', Img)
            if(binaryNum == "0011"):
                binaryNum = "1100"
            else:
                binaryNum = "0011"
    file.close()


# 生成视频
def pictureToMp4(picture_num, fps_, mp4path):
    listtemp=mp4path.split('\\')
    mp4path='/'.join(listtemp)
    fps = fps_  # 帧率
    size = (1840, 1840)  # 需要转为视频的图片的尺寸
    video = cv2.VideoWriter(mp4path, cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), fps, size)
    # 视频保存在当前目录下，格式为.mp4
    for i in range(picture_num):
        item = str(i) + '.jpg'
        img = cv2.imread(item)
        video.write(img)  # 写入视频

    video.release()


class MyFrame(wx.Frame):  # 编写窗口的类
    def __init__(self, parent, id):  # 类的本身属性
        wx.Frame.__init__(self, parent, id, title="图片编码系统", size=(605, 280))
        panel = wx.Panel(self)  # 显示画板
        title = wx.StaticText(panel, label="请在下方填入想要的相关操作", pos=(145, 10))
        font = wx.Font(15, wx.DEFAULT, wx.FONTSTYLE_NORMAL, wx.LIGHT, underline=False)
        tipfont = wx.Font(10, wx.DEFAULT, wx.FONTSTYLE_NORMAL, wx.LIGHT, underline=False)
        title.SetFont(font)
        title.SetForegroundColour("yellow")  # 设置字体的前景色和背景色
        title.SetBackgroundColour("blue")
        
        self.filepath = wx.StaticText(panel, label="请选择文件夹:", pos=(10, 35))
        self.filepath.SetFont(font)
        self.file = wx.TextCtrl(panel, pos=(160, 35), size=(225, 25), style=wx.TE_LEFT)
        self.search = wx.Button(panel, label="浏览文件夹", pos=(400, 33), size=(85, 27))
        #文件夹浏览按钮，选定生成图片所在的文件夹
        self.search.Bind(wx.EVT_BUTTON, self.Onclicksearch)
        
        self.filename1 = wx.StaticText(panel, label="编码文件名：", pos=(10, 70))
        self.filename1.SetFont(font)
        self.encodevalue = wx.TextCtrl(panel, pos=(160, 70), size=(225, 25), style=wx.TE_LEFT)
        self.tip1 = wx.StaticText(panel, label="示例:encode.bin", pos=(400, 75))
        self.tip1.SetFont(tipfont)
        
        self.filename2 = wx.StaticText(panel, label="生成视频名：", pos=(10, 103))
        self.filename2.SetFont(font)
        self.videovalue = wx.TextCtrl(panel,pos=(160,100),size=(225,25),style=wx.TE_LEFT)
        self.tip2 = wx.StaticText(panel, label="示例:text.mp4", pos=(400, 105))
        self.tip2.SetFont(tipfont)
        
        self.time = wx.StaticText(panel, label="视频时长(ns)：", pos=(10, 135))
        self.time.SetFont(font)
        self.timevalue = wx.TextCtrl(panel, pos=(160, 130), size=(225, 25), style=wx.TE_LEFT)
        self.tip3 = wx.StaticText(panel, label="示例:2000(ns)", pos=(400, 136))
        self.tip3.SetFont(tipfont)
        
        self.picsizename = wx.StaticText(panel, label="默认行列像素的值为： 行：", pos=(10, 165))
        self.picsizename.SetFont(font)
        self.picsizex = wx.TextCtrl(panel, pos=(260, 165), size=(35, 25), style=wx.TE_LEFT|wx.TE_READONLY)
        self.picsizenamey = wx.StaticText(panel, label="列:", pos=(300, 165))
        self.picsizenamey.SetFont(font)
        self.picsizex.SetValue("92")
        self.picsizey = wx.TextCtrl(panel, pos=(335, 165), size=(35, 25), style=wx.TE_LEFT|wx.TE_READONLY)
        self.picsizey.SetValue("92")
        
        self.picturenum = wx.StaticText(panel,label='生成图片数目：',pos=(375,165))
        self.picturenum.SetFont(font)#设定字体大小，和上面的一样
        self.picnum = wx.TextCtrl(panel,pos=(515,165),size=(40,24),style=wx.TE_LEFT|wx.TE_READONLY)
        self.picnum.SetValue('0')
        #按钮
        clear = wx.Button(panel, label="清除", pos=(100, 200), size=(90, 37))
        clear.Bind(wx.EVT_BUTTON, self.Onclickclear)
        ok = wx.Button(panel, label="生成", pos=(260, 200), size=(90, 37))
        ok.Bind(wx.EVT_BUTTON, self.Onclickok)
        cancel = wx.Button(panel, label="退出", pos=(420, 200), size=(90, 37))
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
            self.file2.SetValue("")
            self.encodevalue.SetValue("")
            
        cleardialog.Destroy()

    def Onclickok(self,event):#main
        fpath = self.file.GetValue()
        encodepath = fpath+'\\'+self.encodevalue.GetValue()
        mp4path = fpath+'\\'+self.videovalue.GetValue()
        picture_num = int(int(self.timevalue.GetValue())/1000*10)
        fps_ = 10
        try:
            #随机生成encode.bin文件
            getencode(encodepath)
            #生成图片个数，编码
            encode(int(self.picsizex.GetValue()), int(self.picsizey.GetValue()), encodepath,picture_num)
            self.picnum.SetValue(str(picture_num))
            pictureToMp4(picture_num,fps_,mp4path)
            wx.MessageBox("所有文件生成成功!")
        except Exception as e:
            wx.MessageBox("Error:"+str(e))
        
    def Onclicksearch(self, event):
        """浏览文件夹，打开文件夹目录窗口，默认从当前目录开始测算"""
        dlg = wx.DirDialog(self, "选择文件夹", os.getcwd(),style=wx.DD_DEFAULT_STYLE)
        #选定文件，则文件目录显示在第一个TextCtrl中
        if dlg.ShowModal() == wx.ID_OK:
            self.file.SetValue(dlg.GetPath())
            os.chdir(dlg.GetPath())

if __name__ == "__main__":
    app = wx.App()
    frame = MyFrame(parent=None, id=-1)
    frame.Center()
    frame.Show()
    app.MainLoop()