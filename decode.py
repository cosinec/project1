import cpptext
import struct
import os
import cv2
import numpy as np
import time#检测代码运行时间的库

#解码
def decode(filenames,nx,ny,decodePath):
    '''
    运用简单的0->黑，1->白的思想
    '''
    picture_num = filenames.__len__()#获取图片个数
    str_binary = ''
    num_binary = 0
    right="0011"
    p_Number=0
    for k in range(picture_num):
        if(k==0):
            yt=cv2.imread('0.jpg',0)
            yt = cv2.resize(yt, (104, 104), interpolation=cv2.INTER_AREA)
        img = cv2.imread(filenames[k],0)#逐个加载图片
        img = cv2.resize(img, (nx, ny), interpolation=cv2.INTER_AREA)
        ret3,img = cv2.threshold(img,155,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        
        #判断是不是同一张图片：
        temp=''
        for j in range(0,4):
            if(img[8,j]>=0 and img[8,j]<=120):#是黑色点
                temp=temp+'0'
            elif(img[8,j]>=200 and img[8,j]<=255):
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
                           num_binary=0
                        if(img[i,j]==0):#是黑色点
                            str_binary=str_binary+'0'
                            num_binary+=1
                        elif(img[i,j]==255):#白色  
                            str_binary=str_binary+'1'
                            num_binary+=1
                elif(i==8):
                    for j in range(4,nx):
                        if(num_binary==8):
                           str_binary=str_binary+' '
                           num_binary=0
                        if(img[i,j]==0):#是黑色点
                            str_binary=str_binary+'0'
                            num_binary+=1
                        elif(img[i,j]==255):#白色
                            str_binary=str_binary+'1'
                            num_binary+=1
                elif(i>=9 and i<=ny-9):
                    for j in range (nx):
                        if(num_binary==8):
                           str_binary=str_binary+' '
                           num_binary=0
                        if(img[i,j]==0):#是黑色点
                            str_binary=str_binary+'0'
                            num_binary+=1
                        elif(img[i,j]==255):#白色            
                            str_binary=str_binary+'1'
                            num_binary+=1
                elif(i>=ny-8 and i<=ny-1):
                    for j in range (8,nx-8):
                        if(num_binary==8):
                           str_binary=str_binary+' '
                           num_binary=0
                        if(img[i,j]==0):#是黑色点
                            str_binary=str_binary+'0'
                            num_binary+=1
                        elif(img[i,j]==255):#白色           
                            str_binary=str_binary+'1'
                            num_binary+=1
    array = np.array([int(b,2) for b in str_binary.split(' ')])
    length = len(array)
    with open(decodePath,'wb') as f:
        for i in range(length):
            f.write(struct.pack('B',array[i]))
    f.close()
    return p_Number

#剪切视频
def get_image(newmp4):
    video_path = newmp4
    cap = cv2.VideoCapture(video_path)
    if cap.isOpened():# 当成功打开视频时cap.isOpened()返回True,否则返回False
        rate = cap.get(5)# 帧速率
        FrameNumber = cap.get(7) # 视频文件的帧数
        duration = FrameNumber/rate# 帧速率/视频总帧数 是时间，除以60之后单位是分钟
    image_path = r'D:/A_cos/pro1'
    frame = 15
    try:
        os.system('ffmpeg -i  {0} -r {1} -f image2 {2}\%d.png'.format(video_path, frame, image_path))
        print('OK')
    except:
        print('ERROR')

#获得vout.bin
def vout(fpath,decodepath,voutPath,picture_num):
    times = picture_num*980
    fpath1=fpath
    infile = open(fpath1, "rb")
    fpath2=decodepath
    outfile = open(fpath2, "rb")
    fpath3=voutPath
    voutfile = open(fpath3, "wb")
    if infile.closed:
        print("error")
    elif outfile.closed:
        print("error")
    elif voutfile.closed:
        print("error")
    else:
        for i in range(times):
            indate = infile.read(1)
            if not indate:
                break
            indate = int.from_bytes(indate, byteorder='little', signed=True)
            outdate = int.from_bytes(outfile.read(1), byteorder='little', signed=True)
            voutdate = struct.pack('b', (~(indate ^ outdate)))
            voutfile.write(voutdate)
        infile.close()
        outfile.close()
        voutfile.close()

if __name__ == "__main__":
    '''剪切+定位二维码->解码->生成v.bin文件'''
    newmp4 = "newtext.mp4"
    decodePath = "decode1.bin"
    fPath = "encode1.bin"
    voutPath = "v1.bin"
    
    #视频剪切图片
    start_time = time.time()
    get_image(newmp4)  
    
    #计算png图片个数,并传递给decode
    path = r'D:\A_cos\pro1'##存放png图片的位置，这里不同人需要更改
    filelist = os.listdir(path)
    picture_num = 0#统计png个数
    for item in filelist:
        if item.endswith('.png'):
            picture_num += 1
    images = []#用于存储图片信息的string数组
    for i in range(1, picture_num+1):
        images.append(str(i) + ".png")
        
    #视频剪切
    cpptext.getQrcode(picture_num)
    
    #解码
    picture_num = decode(images,90,90,decodePath)
    print(picture_num)
    #生成v.bin
    vout(fPath,decodePath,voutPath,picture_num)
    end_time = time.time()
    #代码所用时间
    print("time:",(end_time-start_time))