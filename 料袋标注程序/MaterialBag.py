from Marking import Marking
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap,QImage
from cv2 import  imread,circle,line,putText,cvtColor,COLOR_RGB2BGR
from os.path import exists 
from os import remove,listdir
from cv2 import  imread,circle,line,putText,cvtColor,COLOR_RGB2BGR
from math import atan,pi
from xml.etree.ElementTree import Element,ElementTree

class MaterialBag(Marking):
    """description of class"""
    def __init__(self):
        super(MaterialBag, self).__init__()
        self.tips()

    def tips(self):
        self.printmessage("**************************************************说明**************************************************",time=False)
        self.printmessage("*****提示*****：请确保打开路径中不含中文，否则图片可能打不开！！！文件格式支持jpg、png",time=False)
        self.printmessage("**操作快捷键**：Q打开文件；A上一张；D下一张；S保存；R重置当前图片；鼠标左击选点、右击撤销上一步",time=False)
        self.printmessage("***操作说明***：图片框鼠标左键依次单击料带四个顶点及长边上的两个点，完成所有料带后保存自动进入下一张",time=False)

    def calculate(self,point):
        xmin=min(point[0][0],point[1][0],point[2][0],point[3][0])
        ymin=min(point[0][1],point[1][1],point[2][1],point[3][1])
        xmax=max(point[0][0],point[1][0],point[2][0],point[3][0])
        ymax=max(point[0][1],point[1][1],point[2][1],point[3][1])
        [X,Y]=[point[4],point[5]] if point[4][1]>point[5][1] else [point[5],point[4]]
        try:
            J=atan((X[1]-Y[1])/(Y[0]-X[0]))*180/pi
        except:
            message="角度计算异常,请撤销或重置"
            self.statusbar.showMessage(message,1000)
            self.printmessage("角度计算异常,请撤销或重置")
            J=0.0
        #J=J+180 if J<0 else J
        return [(xmin,ymin),(xmax,ymax),J],[X,Y]

    def MouseRightPressEvent(self,x,y):
        if len(self.IMGfile)==0:
            return
        if len(self.IMG_TEMP)>1 :
            self.IMG_TEMP.pop()
            if len(self.vertex)==0 and len(self.targets)!=0:
                self.vertex=self.targets.pop()
                self.Draw.pop()
            self.vertex.pop()
            img1=self.IMG_TEMP[-1]
            frame = cvtColor(img1, COLOR_RGB2BGR)
            img = QImage(frame.data, frame.shape[1], frame.shape[0],frame.shape[1]*3, QImage.Format_RGB888)#第四个参数设置通道数对齐,不然图片可能会变形
            self.label.setPixmap(QPixmap.fromImage(img))
            self.label.setScaledContents(True)#图片大小与label适应
            if len(self.vertex)>4:
                message="回撤到第"+str(len(self.targets)+1)+"个料包,第"+str(len(self.vertex)-4)+"个长边上的点。"
            else:
                message="回撤到第"+str(len(self.targets)+1)+"个料包,第"+str(len(self.vertex))+"个顶点。"
            #message="回撤到第"+str(len(self.targets)+1)+"个料包,第"+str(len(self.vertex))+"个点"
            self.statusbar.showMessage(message,5000)
    def MouseLeftPressEvent(self,X,Y):
        if len(self.IMGfile)==0:
            return
        img1=self.IMG_TEMP[-1].copy()
        x=img1.shape[1]*X/self.label.width()
        y=img1.shape[0]*Y/self.label.height()
        img_=circle(img1,center =(int(x),int(y)),radius = 6,color = (0,0,255),thickness = -1)
        self.IMG_TEMP.append(img_)
        frame = cvtColor(img_, COLOR_RGB2BGR)
        img = QImage(frame.data, frame.shape[1], frame.shape[0],frame.shape[1]*3, QImage.Format_RGB888)#第四个参数设置通道数对齐,不然图片可能会变形
        self.label.setPixmap(QPixmap.fromImage(img))
        self.label.setScaledContents(True)#图片大小与label适应
        self.vertex.append((int(x),int(y)))
        #self.printmessage("采集第"+str(len(self.targets)+1)+"个料包,第"+str(len(self.vertex))+"个点")
        if len(self.vertex)==6:
            self.IMG_TEMP.pop()
            self.targets.append(self.vertex.copy())
            drawdata,XY=self.calculate(self.vertex)
            self.vertex.clear()
            iimg=self.Draw[-1].copy()
            self.draw(iimg,drawdata,XY)
            self.Draw.append(iimg)
            self.IMG_TEMP.append(iimg)
            frame = cvtColor(iimg, COLOR_RGB2BGR)
            img = QImage(frame.data, frame.shape[1], frame.shape[0],frame.shape[1]*3, QImage.Format_RGB888)#第四个参数设置通道数对齐,不然图片可能会变形
            self.label.setPixmap(QPixmap.fromImage(img))
            self.label.setScaledContents(True)#图片大小与label适应
            message="完成第"+str(len(self.targets))+"个料包,角度("+str(round(drawdata[2],1))+")"
            self.statusbar.showMessage(message,5000)
        else:
            if len(self.vertex)>=4:
                message="请继续点击第"+str(len(self.targets)+1)+"个料包,第"+str(len(self.vertex)-3)+"个长边上的点，以确定角度。"
            else:
                message="请继续点击第"+str(len(self.targets)+1)+"个料包,第"+str(len(self.vertex)+1)+"个顶点，以框选料带。"
            self.statusbar.showMessage(message,5000)

    def draw(self,img,data,XY):
        line(img,(data[0][0],data[0][1]),(data[0][0],data[1][1]),color=(255,0,0),thickness=int(img.shape[0]/400))
        line(img,(data[0][0],data[0][1]),(data[1][0],data[0][1]),color=(255,0,0),thickness=int(img.shape[0]/400))
        line(img,(data[1][0],data[1][1]),(data[1][0],data[0][1]),color=(255,0,0),thickness=int(img.shape[0]/400))
        line(img,(data[1][0],data[1][1]),(data[0][0],data[1][1]),color=(255,0,0),thickness=int(img.shape[0]/400))
        t= 1 if data[2]>=0 else -1
        step=t*int(((XY[0][0]-XY[1][0])**2+(XY[0][1]-XY[1][1])**2)**0.5)
        line(img,(XY[0][0],XY[0][1]),(XY[1][0],XY[1][1]),color=(0,255,0),thickness=int(img.shape[0]/400))
        line(img,(XY[0][0],XY[0][1]),(XY[0][0]+step,XY[0][1]),color=(0,255,0),thickness=int(img.shape[0]/400))
        img = putText(img, str(round(data[2],1)), (XY[0][0]+t*30, XY[0][1]+30), 0, 0.8, (0, 255, 0), int(img.shape[0]/400))
        img=circle(img,center =(int((data[0][0]+data[1][0])/2),int((data[0][1]+data[1][1])/2)),radius = int(img.shape[0]/150),color = (255,0,255),thickness = -1)
        
    def savexml(self):
        result=[]
        try:
            path=self.folder +"/"+self.IMGfile[self.currentimg][:-3]+"xml"
            f=self.folder[self.folder.rfind("/")+1:]
        except:
            message="未加载图片"
            self.statusbar.showMessage(message,1000)
            #self.printmessage("未加载图片")
            return
        if exists(path):
            remove(path)
        if len(self.targets)!=0:
            for point in self.targets:
                X,_=self.calculate(point)
                result.append(X)
            annotation = Element('annotation')
            tree = ElementTree(annotation)
            folder= Element('folder')
            folder.text=f
            annotation.append(folder)

            filename= Element('filename')
            filename.text=self.IMGfile[self.currentimg]
            annotation.append(filename)

            Path= Element('path')
            Path.text=path.replace("/","\\")
            annotation.append(Path)

            Size= Element('size')
            width= Element('width')
            width.text=str(self.Draw[-1].shape[1])
            Size.append(width)

            height= Element('height')
            height.text=str(self.Draw[-1].shape[0])
            Size.append(height)

            depth= Element('depth')
            depth.text=str(self.Draw[-1].shape[2])
            Size.append(depth)
            annotation.append(Size)
            for r in result:
                object= Element('object')
                name= Element('name')
                name.text='MaterialBag'
                object.append(name)

                bndbox= Element('bndbox')
            
                xmin=Element('xmin')
                xmin.text=str(r[0][0])
                bndbox.append(xmin)
                ymin=Element('ymin')
                ymin.text=str(r[0][1])
                bndbox.append(ymin)

                xmax=Element('xmax')
                xmax.text=str(r[1][0])
                bndbox.append(xmax)
                ymax=Element('ymax')
                ymax.text=str(r[1][1])
                bndbox.append(ymax)
                object.append(bndbox)

                direction=Element('direction')
                direction.text=str(round(r[2],2))
                object.append(direction)
                annotation.append(object)
            self.indent(annotation)
            tree.write(path, xml_declaration=True)
            self.printmessage("已保存"+path)
            message="加载下一张"
            self.statusbar.showMessage(message,1000)
            self.clear()
            self.nextimg()