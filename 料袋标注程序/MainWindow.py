from PyQt5.QtWidgets import QMessageBox,QApplication,QFileDialog,QMainWindow,QWidget
from PyQt5.QtGui import QIcon,QPixmap,QImage
from PyQt5.QtCore import Qt,QCoreApplication
from UmbrellaCone import UmbrellaCone
from MaterialBag import MaterialBag
from MainWindowUI import Ui_Marking


class MainWindow(QWidget,Ui_Marking):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.ENTER)
    def ENTER(self):
        if self.Model.currentText()=="加油口":
            self.run=UmbrellaCone("FuelFiller")
        elif self.Model.currentText()=="伞套":
            self.run=UmbrellaCone("UmbrellaCone")
        elif self.Model.currentText()=="料带":
            self.run=MaterialBag()
            
        else:
            return
        self.run.show()
        self.close()

if __name__=='__main__':
    app = QApplication([])
    stats = MainWindow()
    stats.show()
    app.exec_()