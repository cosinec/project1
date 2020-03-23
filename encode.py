import cv2
import numpy as np
import struct
import random

#随机生成 n个 encode.bin
def getencode(encodePath):
    FILE_NUMBER = 1 #生成5个文件
    MAX_LENGTH = 10240 #10M=10485760B
    for i in range(FILE_NUMBER):
        fpath=encodePath#fpath=encodePath.format(i+1)
        fo = open(fpath, "wb")
        print("FILE", i+1, ":", fpath, "\n")
        length = random.randint(0, MAX_LENGTH) * random.randint(0, MAX_LENGTH) % MAX_LENGTH +1 #文件大小上限10M
        if fo.closed:
            print("error")
        else:
            for x in range(length):
                a = random.randint(-128, 127)
                w = struct.pack('b', a)
                fo.write(w)
            fo.close()
            print("FILE", (i+1), "CREATE OK,LENGTH:", (length/1024/1024), "M\n")

#编码
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

#生成视频
def pictureToMp4(picture_num,fps_,mp4name):
    fps = fps_ #帧率
    size = (1840,1840) #需要转为视频的图片的尺寸
    video = cv2.VideoWriter(mp4name, cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), fps, size)
    #视频保存在当前目录下，格式为.mp4
    for i in range(picture_num):
        item = str(i) + '.jpg'
        img = cv2.imread(item)
        video.write(img)#写入视频

    video.release()


if __name__ == "__main__":
    '''读文件->编码->生成视频'''
    encodepath = "encode1.bin"
    mp4name = "text.mp4"
    timemp4 = "2000"#视频时长，单位ns
    nx,ny = 92,92#尺寸
    picture_num = int(int(timemp4)/1000*10)
    #随机生成二进制文件
    #getencode(encodePath)
    #生成图片个数，编码
    encode(nx, ny,encodepath,picture_num)
    #计算fps
    fps_=10
    #图片转换成视频
    pictureToMp4(picture_num,fps_,mp4name)    