from PyQt5.QtWidgets import QMessageBox,QApplication,QFileDialog,QMainWindow
from PyQt5.QtGui import QIcon,QPixmap,QImage
from PyQt5.QtCore import Qt,QCoreApplication
from os.path import exists 
from os import remove,listdir
from time import strftime,localtime
from cv2 import  imread,circle,line,putText,cvtColor,COLOR_RGB2BGR
from math import atan,pi
from xml.etree.ElementTree import Element,ElementTree
from ui import Ui_MainWindow
class LabelIMG(QMainWindow,Ui_MainWindow):
    """description of class"""
    def __init__(self):
        #self = uic.loadUi("labelimg.ui")
        super(LabelIMG, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("料带标签制作器")
        self.actionOpenFile.triggered.connect(self.OpenFile)
        self.Refreshfolder.triggered.connect(self.OpenFile)
        self.last.clicked.connect(self.lastimg)
        self.next.clicked.connect(self.nextimg)
        self.save.clicked.connect(self.SAVE)
        self.reset.clicked.connect(self.RESET)
        self.label.mousePressEvent=self.___mousePressEvent
        self.IMGfile=[] #图片文件名集合
        self.vertex=[] #一个料带四个顶点加上两个角度点
        self.targets=[] #所有的料带
        self.imgsum=0 #图片总数
        self.currentimg=0 #当前图片索引
        self.IMG_TEMP=[] #画标记时临时存储图片
        self.Draw=[] #画标记时临时存储图片
        self.folder=None #当前图片所在文件夹名
        self.printmessage("**************************************************说明**************************************************",time=False)
        self.printmessage("*****提示*****：请确保打开路径中不含中文，否则图片可能打不开！！！文件格式支持jpg、png",time=False)
        self.printmessage("**操作快捷键**：Q打开文件；A上一张；D下一张；S保存；R重置当前图片；鼠标左击选点、右击撤销上一步",time=False)
        self.printmessage("***操作说明***：图片框鼠标左键依次单击料带四个顶点及长边上的两个点，完成所有料带后保存自动进入下一张",time=False)
    def RESET(self):
        if len(self.IMG_TEMP)!=0 :
            self.clear()
            file_path=self.folder +"/"+self.IMGfile[self.currentimg]
            self.IMG_TEMP.append(imread(file_path))
            img1=self.IMG_TEMP[-1]
            self.Draw.append(imread(file_path))
            frame = cvtColor(img1, COLOR_RGB2BGR)
            img = QImage(frame.data, frame.shape[1], frame.shape[0],frame.shape[1]*3, QImage.Format_RGB888)#第四个参数设置通道数对齐,不然图片可能会变形
            self.label.setPixmap(QPixmap.fromImage(img))
            self.label.setScaledContents(True)#图片大小与label适应
            message="已重置"
            self.statusbar.showMessage(message,1000)
            #self.printmessage("已重置")
    def __indent(self,elem, level=0):
        i = "\n" + level*"\t"
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
               self.__indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
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
    def SAVE(self):
        result=[]
        try:
            path=self.folder +"/"+self.IMGfile[self.currentimg][:-3]+"xml"
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
            folder.text=self.folder
            annotation.append(folder)
            filename= Element('filename')
            filename.text=self.IMGfile[self.currentimg]
            annotation.append(filename)
            Path= Element('path')
            Path.text=path
            annotation.append(Path)
            for r in result:
                bag = Element('bag')
                leftup=Element('leftup')
                x=Element('x')
                y=Element('y')
                x.text,y.text=str(r[0][0]),str(r[0][1])
                leftup.append(x)
                leftup.append(y)
                bag.append(leftup)
                rightdown=Element('rightdown')
                x=Element('x')
                y=Element('y')
                x.text,y.text=str(r[1][0]),str(r[1][1])
                rightdown.append(x)
                rightdown.append(y)
                bag.append(rightdown)
                joint=Element('joint')
                joint.text=str(round(r[2],2))
                bag.append(joint)
                annotation.append(bag)
            self.__indent(annotation)
            tree.write(path, xml_declaration=True)
            self.printmessage("已保存"+path)
            message="加载下一张"
            self.statusbar.showMessage(message,1000)
            self.nextimg()

    def OpenFile(self):
        self.imgsum=0
        self.clear()
        self.IMGfile.clear()
        self.currentimg=0
        if self.folder is None:
            self.folder=QFileDialog.getExistingDirectory(self, "选择文件夹", "/")
        if self.folder=='':
            message="取消加载文件夹"
            self.statusbar.showMessage(message,1000)
            self.folder=None
            return 
        dir_files = listdir(self.folder)
        self.printmessage("已打开"+self.folder)
        for file in dir_files:
            if len(file)>4 and (file[-4:]==".jpg" or file[-4:]==".png"):
                self.IMGfile.append(file)
        self.imgsum=len(self.IMGfile)
        exi=[]
        unexi=[]
        while self.currentimg<self.imgsum :
            path=self.folder +"/"+self.IMGfile[self.currentimg][:-3]+"xml"
            if exists(path):
                exi.append(self.IMGfile[self.currentimg])
            else:
                unexi.append(self.IMGfile[self.currentimg])
            self.currentimg+=1
        self.IMGfile=exi+unexi
        self.currentimg=len(exi)
        if len(unexi)==0:
            Existstr="(已有标签)"
        else:
            Existstr="(未做标签)"
        self.printmessage("图片文件共"+str(self.imgsum)+"个，其中"+str(self.currentimg)+"个已做标签")
        title="当前文件("+str(self.currentimg+1)+"/"+str(self.imgsum)+"):"+self.IMGfile[self.currentimg]+Existstr
        _translate = QCoreApplication.translate
        self.groupBox.setTitle(_translate("MainWindow", title))
        #self.printmessage("当前文件("+str(self.currentimg+1)+"/"+str(self.imgsum)+"):"+self.IMGfile[self.currentimg]+Existstr)
        if self.imgsum!=0:
            self.label.setPixmap(QPixmap(self.folder+"/"+self.IMGfile[self.currentimg]))
            self.label.setScaledContents(True)#图片大小与label适应

        file_path=self.folder +"/"+self.IMGfile[self.currentimg]
        self.IMG_TEMP.append(imread(file_path)) 
        self.Draw.append(imread(file_path)) 
    def lastimg(self):
        if self.folder is not None and self.currentimg>0:
            self.currentimg-=1
            self.label.setPixmap(QPixmap(self.folder +"/"+self.IMGfile[self.currentimg]))
            self.label.setScaledContents(True)#图片大小与label适应
            path=self.folder +"/"+self.IMGfile[self.currentimg][:-3]+"xml"
            if exists(path):
                Existstr="(已有标签)"
            else:
                Existstr="(未做标签)"
            title="当前文件("+str(self.currentimg+1)+"/"+str(self.imgsum)+"):"+self.IMGfile[self.currentimg]+Existstr
            _translate = QCoreApplication.translate
            self.groupBox.setTitle(_translate("MainWindow", title))
            #self.printmessage("当前文件("+str(self.currentimg+1)+"/"+str(self.imgsum)+"):"+self.IMGfile[self.currentimg]+Existstr)
            self.clear()
            file_path=self.folder +"/"+self.IMGfile[self.currentimg]
            self.IMG_TEMP.append(imread(file_path))
            self.Draw.append(imread(file_path))
        elif len(self.IMGfile)==0:
            message="未加载图片"
            self.statusbar.showMessage(message,1000)
            #self.printmessage("未加载图片")
        else:
            message="已经是第一个文件了"
            self.statusbar.showMessage(message,1000)
            #self.printmessage("已经是第一个文件了")
    def nextimg(self):
        if self.folder is not None and self.currentimg<self.imgsum-1:
            self.currentimg+=1
            self.label.setPixmap(QPixmap(self.folder +"/"+self.IMGfile[self.currentimg]))
            self.label.setScaledContents(True)#图片大小与label适应
            path=self.folder +"/"+self.IMGfile[self.currentimg][:-3]+"xml"
            if exists(path):
                Existstr="(已有标签)"
            else:
                Existstr="(未做标签)"
            title="当前文件("+str(self.currentimg+1)+"/"+str(self.imgsum)+"):"+self.IMGfile[self.currentimg]+Existstr
            _translate = QCoreApplication.translate
            self.groupBox.setTitle(_translate("MainWindow", title))
            #self.printmessage("当前文件("+str(self.currentimg+1)+"/"+str(self.imgsum)+"):"+self.IMGfile[self.currentimg]+Existstr)
            self.clear()
            file_path=self.folder +"/"+self.IMGfile[self.currentimg]
            self.IMG_TEMP.append(imread(file_path))
            self.Draw.append(imread(file_path))
        elif len(self.IMGfile)==0:
            message="未加载图片"
            self.statusbar.showMessage(message,1000)
            #self.printmessage("未加载图片")
        else:
            message="已经是最后一个文件了"
            self.statusbar.showMessage(message,1000)
            #self.printmessage("已经是最后一个文件了")
    def ___mousePressEvent(self,event):
        '''
        n = event.button() # 用来判断是哪个鼠标健触发了事件【返回值：0 1 2 4】
        Qt.NoButton - 0 - 没有按下鼠标键
        Qt.LeftButton - 1 -按下鼠标左键
        Qt.RightButton - 2 -按下鼠标右键
        Qt.Mion 或 Qt.MiddleButton -4 -按下鼠标中键
        '''
        if len(self.IMGfile)==0:
            return
        #if event.x()<0 or event.x()>640 or event.y()<0 or event.y()>360:
        #    return
        if event.button()==Qt.RightButton and len(self.IMG_TEMP)>1 :
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
            #self.printmessage("回撤到第"+str(len(self.targets)+1)+"个料包,第"+str(len(self.vertex))+"个点")
        if event.button()==Qt.LeftButton :
            img1=self.IMG_TEMP[-1].copy()
            x=img1.shape[1]*event.x()/self.label.width()
            y=img1.shape[0]*event.y()/self.label.height()
            img_=circle(img1,center =(int(x),int(y)),radius = 6,color = (0,0,255),thickness = 2)
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
                self.drawline(iimg,drawdata,XY)
                self.Draw.append(iimg)
                self.IMG_TEMP.append(iimg)
                frame = cvtColor(iimg, COLOR_RGB2BGR)
                img = QImage(frame.data, frame.shape[1], frame.shape[0],frame.shape[1]*3, QImage.Format_RGB888)#第四个参数设置通道数对齐,不然图片可能会变形
                self.label.setPixmap(QPixmap.fromImage(img))
                self.label.setScaledContents(True)#图片大小与label适应
                message="完成第"+str(len(self.targets))+"个料包,角度("+str(round(drawdata[2],1))+")"
                self.statusbar.showMessage(message,5000)
                #self.printmessage("完成第"+str(len(self.targets)+1)+"个料包,角度("+str(round(drawdata[2],1))+")")
            else:
                if len(self.vertex)>=4:
                    message="请继续点击第"+str(len(self.targets)+1)+"个料包,第"+str(len(self.vertex)-3)+"个长边上的点，以确定角度。"
                else:
                    message="请继续点击第"+str(len(self.targets)+1)+"个料包,第"+str(len(self.vertex)+1)+"个顶点，以框选料带。"
                self.statusbar.showMessage(message,5000)
    def drawline(self,img,data,XY):
        line(img,(data[0][0],data[0][1]),(data[0][0],data[1][1]),color=(255,0,0),thickness=2)
        line(img,(data[0][0],data[0][1]),(data[1][0],data[0][1]),color=(255,0,0),thickness=2)
        line(img,(data[1][0],data[1][1]),(data[1][0],data[0][1]),color=(255,0,0),thickness=2)
        line(img,(data[1][0],data[1][1]),(data[0][0],data[1][1]),color=(255,0,0),thickness=2)
        t= 1 if data[2]>=0 else -1
        step=t*int(((XY[0][0]-XY[1][0])**2+(XY[0][1]-XY[1][1])**2)**0.5)
        line(img,(XY[0][0],XY[0][1]),(XY[1][0],XY[1][1]),color=(0,255,0),thickness=2)
        line(img,(XY[0][0],XY[0][1]),(XY[0][0]+step,XY[0][1]),color=(0,255,0),thickness=2)
        img = putText(img, str(round(data[2],1)), (XY[0][0]+t*30, XY[0][1]+30), 0, 1.2, (0, 255, 0), 2)
        img=circle(img,center =(int((data[0][0]+data[1][0])/2),int((data[0][1]+data[1][1])/2)),radius = 3,color = (0,255,255),thickness = 5)
    def printmessage(self,message,time=True):
        textCursor = self.Message.textCursor()
        textCursor.movePosition(textCursor.End)
        self.Message.setTextCursor(textCursor)
        if time:
            prostr='<'+str(strftime("%H:%M:%S", localtime()))+'> :'
        else:
            prostr=''
        self.Message.insertPlainText(prostr+message+"\r\n")
        textCursor.movePosition(textCursor.End)
        self.Message.setTextCursor(textCursor)

    def clear(self):
        self.targets.clear()
        self.IMG_TEMP.clear()
        self.vertex.clear()
        self.Draw.clear()
if __name__ == '__main__':
    app = QApplication([])
    main = LabelIMG()
    main.show()
    app.exec_()


