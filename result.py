import cpptext
import numpy as np
import cv2
import copy
import os
import time#检测代码运行时间的库

def fileread(filename1): #读取用户的二进制文件并进行编码处理
    with open(filename1,'rb') as file:
        str1 = str(file.read())[2:-1]#读文件并截取字符串去掉 b''的部分
        lenstr1 = len(str1)#长度
        i = 0#str1字符串下标
        result = ''#用于存储二进制结果。8位二进制
        while lenstr1:
            if (ord(str1[i])>=32 and ord(str1[i])<=63):
                temp = ' '.join([bin(ord(str1[i])).replace('0b', '0')])
            else:
                temp = ' '.join([bin(ord(str1[i])).replace('0b', '')])
            result = result + temp#字符串拼接
            i += 1
            lenstr1 -= 1
    file.close()
    return result

def encode(nx,ny,strs):
    '''对图片处理，把导入的字符串插入'''
    value=0#strs字符串下标
    picture_num = 0#图片数量
    length = len(strs)#二进制字符串长度
    binaryNum = "0011"#图片筛选标志
    while True:
        ##生成一张白色图片，随后对相关的项目进行改动
        Img = np.zeros((nx,ny),dtype = np.uint8)+255
        
        #判断标志
        lenNum = len(binaryNum)
        for k in range(lenNum):
            if(binaryNum[k]=='0'):
                Img[9][k+1] = 0
                
        ##绘制定位点
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
                    
        if(i == nx-2 and length > 0):#没有读取完毕
            #放大像素点
            Img = cv2.resize(Img, (int(ny*20), int(nx*20)), interpolation=cv2.INTER_NEAREST)
            #cv2.imshow('image',Img)
            #cv2.waitKey()
            #写入图片
            cv2.imwrite(str(picture_num)+'.jpg', Img)
            picture_num += 1#图片数量增加1
            if(binaryNum == "0011"):
                binaryNum = "1100"
            else:
                binaryNum = "0011"
        else:#读取完毕
            #放大像素点
            binaryNum = "1010"
            k=0
            for k in range(4):
                if(binaryNum[k]=='0'):
                    Img[9][k+1] = 0
                else:
                    Img[9][k+1] = 255
            Img = cv2.resize(Img, (int(ny*20), int(nx*20)),interpolation=cv2.INTER_NEAREST)
            cv2.imwrite(str(picture_num)+'.jpg', Img)
            picture_num += 1#图片数量增加1
            break
    return picture_num

def decode(filenames,nx,ny):
    '''
    运用简单的0->黑，1->白的思想
    '''
    picture_num = filenames.__len__()#获取图片个数
    str_binary = ''
    num_binary = 0
    right="0011"
    endcode=0
    flag = 0  #结束标志
    for k in range(picture_num):
        if(flag==1):
            break
        if(k==10):
            yt = cv2.imread('7.jpg',0)
            yt = cv2.resize(yt,(80,80),interpolation=cv2.INTER_AREA)
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
        if(temp==right or temp=="1010"):
            samepicture=0
            if(right=="0011"):
                right="1100"
            elif(right=="1100"):
                right="0011"
        else:samepicture=1
        #开始解码 遍历所有像素
        if(samepicture==0):
            for i in range(ny):
                if(flag):
                    break
                if(i>=0 and i<=7):
                    for j in range(8,nx-8):
                        if(endcode==7 and temp=="1010"):#结束点
                              flag=1
                              break
                        if(num_binary==7):
                           str_binary=str_binary+' '
                           num_binary=0
                           endcode=0
                        if(img[i,j]>=0 and img[i,j]<=120):#是黑色点
                            endcode=0
                            str_binary=str_binary+'0'
                            num_binary+=1
                        elif(img[i,j]>=200 and img[i,j]<=255):#白色
                            endcode+=1
                            str_binary=str_binary+'1'
                            num_binary+=1
                elif(i==8):
                    for j in range(4,nx):
                        if(endcode==7 and temp=="1010"):#结束点
                              flag=1
                              break
                        if(num_binary==7):
                           str_binary=str_binary+' '
                           num_binary=0
                           endcode=0
                        if(img[i,j]>=0 and img[i,j]<=120):#是黑色点
                            str_binary=str_binary+'0'
                            endcode=0
                            num_binary+=1
                        elif(img[i,j]>=200 and img[i,j]<=255):#白色
                            endcode+=1
                            str_binary=str_binary+'1'
                            num_binary+=1
                elif(i>=9 and i<=ny-9):
                    for j in range (nx):
                        if(endcode==7 and temp=="1010"):#结束点
                              flag=1
                              break
                        if(num_binary==7):
                           str_binary=str_binary+' '
                           num_binary=0
                           endcode=0
                        if(img[i,j]>=0 and img[i,j]<=120):#是黑色点
                            str_binary=str_binary+'0'
                            endcode=0
                            num_binary+=1
                        elif(img[i,j]>=200 and img[i,j]<=255):#白色
                            endcode+=1
                            str_binary=str_binary+'1'
                            num_binary+=1
                elif(i>=ny-8 and i<=ny-1):
                    for j in range (8,nx-8):
                        if(endcode==7 and temp=="1010"):#结束点
                              flag=1
                              break
                        if(num_binary==7):
                           str_binary=str_binary+' '
                           num_binary=0
                           endcode=0
                        if(img[i,j]>=0 and img[i,j]<=120):#是黑色点
                            endcode=0
                            str_binary=str_binary+'0'
                            num_binary+=1
                        elif(img[i,j]>=200 and img[i,j]<=255):#白色
                            endcode+=1
                            str_binary=str_binary+'1'
                            num_binary+=1
    str_binary=str_binary[:-8]
    str_ascii = ''.join([chr(i) for i in [int(b, 2) for b in str_binary.split(' ')]])
    print(str_ascii)#输出
    with open("decode.bin",'wb') as f:
        f.write(str_ascii.encode())
    f.close()
    return k,i,j

#提取所有轮廓
def detecte(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)
    img, contours, hierachy = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return image, contours, hierachy

#检查最外面的轮廓和中间子轮廓的比例
def compute_1(contours, i, j):
    area1 = cv2.contourArea(contours[i])
    area2 = cv2.contourArea(contours[j])
    if area2 == 0:
        return False
    ratio = area1 * 1.0 / area2
    if abs(ratio - 49.0 / 25):
        return True
    return False

#检查中间子轮廓和最里面子轮廓的比例
def compute_2(contours, i, j):
    area1 = cv2.contourArea(contours[i])
    area2 = cv2.contourArea(contours[j])
    if area2 == 0:
        return False
    ratio = area1 * 1.0 / area2
    if abs(ratio - 25.0 / 9):
        return True
    return False

#计算轮廓中心点
def compute_center(contours, i):
    M = cv2.moments(contours[i])
    cx = int(M['m10'] / M['m00'])
    cy = int(M['m01'] / M['m00'])
    return cx, cy

#检查这个轮廓和它的中间子轮廓以及最里面子轮廓的中心的间距
def detect_contours(vec):
    distance_1 = np.sqrt((vec[0] - vec[2]) ** 2 + (vec[1] - vec[3]) ** 2)
    distance_2 = np.sqrt((vec[0] - vec[4]) ** 2 + (vec[1] - vec[5]) ** 2)
    distance_3 = np.sqrt((vec[2] - vec[4]) ** 2 + (vec[3] - vec[5]) ** 2)
    if sum((distance_1, distance_2, distance_3)) / 3 < 3:
        return True
    return False

def juge_angle(rec):
    if len(rec) < 4:
        return -1, -1, -1, -1
    for i in range(len(rec)):
        for j in range(i + 1, len(rec)):
            for k in range(j + 1, len(rec)):
                for m in range(j + 1, len(rec)):
                    distance_1 = np.sqrt((rec[i][0] - rec[j][0]) ** 2 + (rec[i][1] - rec[j][1]) ** 2)
                    distance_2 = np.sqrt((rec[i][0] - rec[k][0]) ** 2 + (rec[i][1] - rec[k][1]) ** 2)
                    distance_3 = np.sqrt((rec[j][0] - rec[k][0]) ** 2 + (rec[j][1] - rec[k][1]) ** 2)
                    distance_4 = np.sqrt((rec[i][0] - rec[m][0]) ** 2 + (rec[i][1] - rec[m][1]) ** 2)
                    distance_5 = np.sqrt((rec[j][0] - rec[m][0]) ** 2 + (rec[j][1] - rec[m][1]) ** 2)
                    flag = 0
                    if m != k:
                        if abs(distance_1 - distance_2) < 5:
                            if abs(np.sqrt(np.square(distance_1) + np.square(distance_2)) - distance_3) < 5:
                                flag = 1
                        elif abs(distance_1 - distance_3) < 5:
                            if abs(np.sqrt(np.square(distance_1) + np.square(distance_3)) - distance_2) < 5:
                                flag = 1
                        elif abs(distance_2 - distance_3) < 5:
                            if abs(np.sqrt(np.square(distance_2) + np.square(distance_3)) - distance_1) < 5:
                                flag = 1
                        if flag == 1:
                            if abs(distance_1 - distance_4) < 5:
                                if abs(np.sqrt(np.square(distance_1) + np.square(distance_4)) - distance_5) < 5:
                                    return i, j, k, m
                            elif abs(distance_1 - distance_5) < 5:
                                if abs(np.sqrt(np.square(distance_1) + np.square(distance_5)) - distance_4) < 5:
                                    return i, j, k, m
                            elif abs(distance_4 - distance_5) < 5:
                                if abs(np.sqrt(np.square(distance_4) + np.square(distance_4)) - distance_1) < 5:
                                    return i, j, k, m
    return -1, -1, -1, -1

def find(image,contours,hierachy,newimpath):
    '''找到符合要求的轮廓'''
    rec=[]
    for i in range(len(hierachy)):
        child = hierachy[i][2]
        child_child=hierachy[child][2]
        if child!=-1 and hierachy[child][2]!=-1:
            if compute_1(contours, i, child) and compute_2(contours,child,child_child):
                cx1,cy1=compute_center(contours,i)
                cx2,cy2=compute_center(contours,child)
                cx3,cy3=compute_center(contours,child_child)
                if detect_contours([cx1,cy1,cx2,cy2,cx3,cy3]):
                    rec.append([cx1,cy1,cx2,cy2,cx3,cy3,i,child,child_child])
    '''计算得到所有在比例上符合要求的轮廓中心点'''
    i,j,k,m=juge_angle(rec)
    if i==-1 or j== -1 or k==-1 or m==-1:
        return
    bottom1Xs,bottom1Ys = getXsYs(contours[rec[i][6]])
    bottom2Xs,bottom2Ys = getXsYs(contours[rec[j][6]])
    top1Xs,top1Ys = getXsYs(contours[rec[m][6]])
    top2Xs,top2Ys = getXsYs(contours[rec[k][6]])
    if min(bottom1Xs)<min(bottom2Xs):
        bottomLeftXs = bottom1Xs
        bottomLeftYs = bottom1Ys
        bottomRightXs = bottom2Xs
        bottomRightYs = bottom2Ys
    else:
        bottomLeftXs = bottom2Xs
        bottomLeftYs = bottom2Ys
        bottomRightXs = bottom1Xs
        bottomRightYs = bottom1Ys
    if min(top1Xs)<min(top2Xs):
        topLeftXs = top1Xs
        topLeftYs = top1Ys
        topRightXs = top2Xs
        topRightYs = top2Ys
    else:
        topLeftXs = top2Xs
        topLeftYs = top2Ys
        topRightXs = top1Xs
        topRightYs = top1Ys
    bottomLeft = [min(bottomLeftXs),max(bottomLeftYs)]#左下
    topLeft = [min(topLeftXs),min(topLeftYs)]#左上
    bottomRight = [max(bottomRightXs),max(bottomRightYs)]#右下
    topRight = [max(topRightXs),min(topRightYs)]#右上
    
    HW= int(max(bottomRightXs))-int(min(bottomLeftXs))
    # 原图中书本的四个角点(左上、右上、左下、右下),与变换后矩阵位置
    pts1 = np.float32([topLeft,topRight,bottomLeft,bottomRight])
    pts2 = np.float32([[0, 0],[HW,0],[0, HW],[HW,HW]])
    
    # 生成透视变换矩阵；进行透视变换
    M = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(image, M, (HW, HW))
    #cv2.imshow("result",dst)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    cv2.imwrite(newimpath, dst)
    
    return

    
def getXsYs(listcontours):
    points = [i[0] for i in listcontours]
    Xs = [i[0] for i in points]
    Ys = [i[1] for i in points]
    return Xs,Ys

def pictureToMp4(picture_num):
    fps = 13 #帧率
    size = (1600,1600) #需要转为视频的图片的尺寸
    #可以使用cv2.resize()进行修改
    
    video = cv2.VideoWriter("text.mp4", cv2.VideoWriter_fourcc('m', 'p', '4', 'v'), fps, size)
    #视频保存在当前目录下，格式为.mp4
    
    for i in range(picture_num):
        item = str(i) + '.jpg'
        img = cv2.imread(item)
        video.write(img)#写入视频

    video.release()

def get_image():
    video_path = r'newtext.mp4'
    cap = cv2.VideoCapture(video_path)
    if cap.isOpened():# 当成功打开视频时cap.isOpened()返回True,否则返回False
        rate = cap.get(5)# 帧速率
        FrameNumber = cap.get(7) # 视频文件的帧数
        duration = FrameNumber/rate# 帧速率/视频总帧数 是时间，除以60之后单位是分钟
    image_path = r'D:/A_cos/pro1'
    frame = 13
    try:
        os.system('ffmpeg -i  {0} -r {1} -f image2 {2}\%d.png'.format(video_path, frame, image_path))
        print('OK')
    except:
        print('ERROR')



if __name__ == "__main__":
    '''读文件->编码->生成视频'''
    #读文件
    #str_ebinary = fileread(r"encode.bin")
    #生成图片个数，编码
    nx,ny = 80,80#尺寸
    #picture_num = encode(nx, ny,str_ebinary)
    #图片转换成视频
    #pictureToMp4(picture_num)
    
    start_time = time.time()
    '''定位二维码->解码'''
    #视频剪切图片
    #get_image()
    path = r'D:\A_cos\pro1'
    filelist = os.listdir(path)
    
    #计算png图片个数
    picture_num = 0
    for item in filelist:
        if item.endswith('.png'):
            picture_num += 1
            
    #用images保存图片信息,y用于解码
    images = []#用于存储图片信息的string数组
    for i in range(1, picture_num+1):
        images.append(str(i) + ".png")
        
    cpptext.getQrcode(picture_num)
    #摆正剪切出二维码
    #for i in range(picture_num):
        #imgpath = newimpath = images[i]
        #image = cv2.imread(imgpath)
        #image = reshape_image(image)
        #image, contours, hierachy = detecte(image)
        #find(image, contours, np.squeeze(hierachy), newimpath)
    
    #解码
    num,y,x= decode(images,nx-2,ny-2)
    print(num,"\t",y,"\t",x)
    #清除所有窗口
    #cv2.destroyAllWindows()
    end_time = time.time()
    #代码所用时间
    print("time:",(end_time-start_time))
