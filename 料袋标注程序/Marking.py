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
class Marking(QMainWindow,Ui_MainWindow):
    """标注类，需要子类重载calculate、save、___mousePressEvent、draw函数"""
    def __init__(self):
        super(Marking, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("标注软件")
        self.IMGfile=[] #图片文件名集合
        self.imgsum=0 #图片总数
        self.currentimg=0 #当前图片索引

        self.targets=[] #当前图所有对象历史标注操作的数据堆栈
        self.vertex=[] #当前对象历史标注操作的数据堆栈
    
        self.IMG_TEMP=[] #当前对象历史标注操作的图片堆栈
        self.Draw=[] #当前图所有对象历史标注操作的图片堆栈
        self.folder=None #当前图片所在文件夹名

        self.actionOpenFile.triggered.connect(self.openfolder)
        self.Refreshfolder.triggered.connect(self.refreshfolder)
        self.last.clicked.connect(self.lastimg)
        self.next.clicked.connect(self.nextimg)
        self.save.clicked.connect(self.savexml)
        self.reset.clicked.connect(self.resetoperate)
        self.label.mousePressEvent=self.___mousePressEvent

    def tips(self):
        #提示信息
        pass

    def indent(self,elem, level=0):
    #写入MXL文件的格式

        i = "\n" + level*"\t"
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
               self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def calculate(self):
        #子类重写，用于实现标注中相应的计算
        return None

    def savexml(self):
        #用于保存标注结果，XML文件
        pass

    def openfolder(self):
        #打开文件夹
        foldername=self.folder
        self.folder=None
        self.refreshfolder()
        if self.folder==None:
            self.folder=foldername

    def refreshfolder(self):
        #刷新当前文件夹
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
        #图片上翻页
        if self.folder is not None and self.currentimg>0:
            if len(self.targets)!=0 or len(self.vertex)!=0:
                if QMessageBox.question(self,"提示","尚未保存，是否舍弃当前操作？",QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes) != QMessageBox.Yes:
                    return
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
        else:
            message="已经是第一个文件了"
            self.statusbar.showMessage(message,1000)

    def nextimg(self):
        #下翻页
        if self.folder is not None and self.currentimg<self.imgsum-1:
            if len(self.targets)!=0 or len(self.vertex)!=0:
                if QMessageBox.question(self,"提示","尚未保存，是否舍弃当前操作？",QMessageBox.Yes|QMessageBox.No,QMessageBox.Yes) != QMessageBox.Yes:
                    return
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

    def MouseLeftPressEvent(self,x,y):
        #鼠标回调，子对象重写
        pass

    def MouseRightPressEvent(self,x,y):
        #鼠标回调，子对象重写
        pass

    def ___mousePressEvent(self,event):
        '''
        n = event.button() # 用来判断是哪个鼠标健触发了事件【返回值：0 1 2 4】
        Qt.NoButton - 0 - 没有按下鼠标键
        Qt.LeftButton - 1 -按下鼠标左键
        Qt.RightButton - 2 -按下鼠标右键
        Qt.Mion 或 Qt.MiddleButton -4 -按下鼠标中键
        '''
        x,y=event.x(),event.y()
        if event.button()==Qt.LeftButton:
            self.MouseLeftPressEvent(x,y)
        elif event.button()==Qt.RightButton:
            self.MouseRightPressEvent(x,y)
        else:
            pass

    def draw(self,img,data):
        #画标注结果，子对象重写
        pass

    def printmessage(self,message,time=True):
        #消息打印
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
        #清除数据
        self.targets.clear()
        self.IMG_TEMP.clear()
        self.vertex.clear()
        self.Draw.clear()

    def resetoperate(self):
        #重置当前标定数据
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