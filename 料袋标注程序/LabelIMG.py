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
        self.Refreshfolder.triggered.connect(self.refreshfolder)
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
        self.printmessage("***操作说明***：图片框鼠标左键依次单击伞套上下左右四点和中心点，保存自动进入下一张",time=False)
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
        return [(xmin,ymin),(xmax,ymax),(point[4][0],point[4][1])]

    def SAVE(self):
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
        if len(self.vertex)==5:
            result=self.calculate(self.vertex)
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

            object= Element('object')
            name= Element('name')
            #name.text='UmbrellaCone'
            name.text='FuelFiller'
            object.append(name)

            bndbox= Element('bndbox')
            
            xmin=Element('xmin')
            xmin.text=str(result[0][0])
            bndbox.append(xmin)
            ymin=Element('ymin')
            ymin.text=str(result[0][1])
            bndbox.append(ymin)

            xmax=Element('xmax')
            xmax.text=str(result[1][0])
            bndbox.append(xmax)
            ymax=Element('ymax')
            ymax.text=str(result[1][1])
            bndbox.append(ymax)
            object.append(bndbox)

            center=Element('center')
            x=Element('x')
            y=Element('y')
            x.text,y.text=str(result[2][0]),str(result[2][1])
            center.append(x)
            center.append(y)
            object.append(center)
            annotation.append(object)
            self.__indent(annotation)
            tree.write(path, xml_declaration=True)
            self.printmessage("已保存"+path)
            message="加载下一张"
            self.statusbar.showMessage(message,1000)
            self.nextimg()

    def OpenFile(self):
        filename=self.folder
        self.folder=None
        self.refreshfolder()
        if self.folder==None:
            self.folder=filename
    def refreshfolder(self):
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
        if self.currentimg==self.imgsum:
            self.currentimg=0
        title="当前文件("+str(self.currentimg+1)+"/"+str(self.imgsum)+"):"+self.IMGfile[self.currentimg]+Existstr
        _translate = QCoreApplication.translate
        self.groupBox.setTitle(_translate("MainWindow", title))
       
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
            self.vertex.pop()
            img1=self.IMG_TEMP[-1]
            frame = cvtColor(img1, COLOR_RGB2BGR)
            img = QImage(frame.data, frame.shape[1], frame.shape[0],frame.shape[1]*3, QImage.Format_RGB888)#第四个参数设置通道数对齐,不然图片可能会变形
            self.label.setPixmap(QPixmap.fromImage(img))
            self.label.setScaledContents(True)#图片大小与label适应

            message="回撤到第"+str(len(self.vertex))+"个点。"
            self.statusbar.showMessage(message,5000)

        if event.button()==Qt.LeftButton and len(self.vertex)<5 :
            img1=self.IMG_TEMP[-1].copy()
            x=img1.shape[1]*event.x()/self.label.width()
            y=img1.shape[0]*event.y()/self.label.height()
            img_=circle(img1,center =(int(x),int(y)),radius = int(img1.shape[0]/150),color = (0,0,255),thickness = int(img1.shape[0]/450))
            self.IMG_TEMP.append(img_)
            frame = cvtColor(img_, COLOR_RGB2BGR)
            img = QImage(frame.data, frame.shape[1], frame.shape[0],frame.shape[1]*3, QImage.Format_RGB888)#第四个参数设置通道数对齐,不然图片可能会变形
            self.label.setPixmap(QPixmap.fromImage(img))
            self.label.setScaledContents(True)#图片大小与label适应
            self.vertex.append((int(x),int(y)))
            if len(self.vertex)==5:
                self.IMG_TEMP.pop()
                drawdata=self.calculate(self.vertex)
                iimg=self.Draw[-1].copy()
                self.drawline(iimg,drawdata)
                self.IMG_TEMP.append(iimg)
                frame = cvtColor(iimg, COLOR_RGB2BGR)
                img = QImage(frame.data, frame.shape[1], frame.shape[0],frame.shape[1]*3, QImage.Format_RGB888)#第四个参数设置通道数对齐,不然图片可能会变形
                self.label.setPixmap(QPixmap.fromImage(img))
                self.label.setScaledContents(True)#图片大小与label适应
                message="完成"
                self.statusbar.showMessage(message,5000)
            else:
                message="请继续点击第"+str(len(self.vertex)+1)+"个点。"
                self.statusbar.showMessage(message,5000)
    def drawline(self,img,data):
        line(img,(data[0][0],data[0][1]),(data[0][0],data[1][1]),color=(255,0,0),thickness=int(img.shape[0]/450))
        line(img,(data[0][0],data[0][1]),(data[1][0],data[0][1]),color=(255,0,0),thickness=int(img.shape[0]/450))
        line(img,(data[1][0],data[1][1]),(data[1][0],data[0][1]),color=(255,0,0),thickness=int(img.shape[0]/450))
        line(img,(data[1][0],data[1][1]),(data[0][0],data[1][1]),color=(255,0,0),thickness=int(img.shape[0]/450))
        img=circle(img,center =(data[2][0],data[2][1]),radius = int(img.shape[0]/150),color = (0,0,255),thickness = int(img.shape[0]/450))

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


