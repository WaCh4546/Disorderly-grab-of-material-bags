# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindowUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Marking(object):
    def setupUi(self, Marking):
        Marking.setObjectName("Marking")
        Marking.resize(332, 237)
        self.pushButton = QtWidgets.QPushButton(Marking)
        self.pushButton.setGeometry(QtCore.QRect(200, 190, 121, 31))
        self.pushButton.setObjectName("pushButton")
        self.Model = QtWidgets.QComboBox(Marking)
        self.Model.setGeometry(QtCore.QRect(90, 190, 101, 31))
        font = QtGui.QFont()
        font.setFamily("3ds")
        font.setPointSize(9)
        self.Model.setFont(font)
        self.Model.setAutoFillBackground(True)
        self.Model.setLocale(QtCore.QLocale(QtCore.QLocale.Chinese, QtCore.QLocale.China))
        self.Model.setObjectName("Model")
        self.Model.addItem("")
        self.Model.addItem("")
        self.Model.addItem("")
        self.label = QtWidgets.QLabel(Marking)
        self.label.setGeometry(QtCore.QRect(120, 0, 121, 31))
        font = QtGui.QFont()
        font.setFamily("3ds")
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Marking)
        self.label_2.setGeometry(QtCore.QRect(10, 30, 54, 12))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Marking)
        self.label_3.setGeometry(QtCore.QRect(20, 40, 301, 31))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Marking)
        self.label_4.setGeometry(QtCore.QRect(10, 90, 71, 16))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(Marking)
        self.label_5.setGeometry(QtCore.QRect(20, 100, 61, 31))
        self.label_5.setObjectName("label_5")
        self.label_7 = QtWidgets.QLabel(Marking)
        self.label_7.setGeometry(QtCore.QRect(180, 100, 61, 31))
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(Marking)
        self.label_8.setGeometry(QtCore.QRect(250, 100, 61, 31))
        self.label_8.setObjectName("label_8")
        self.label_9 = QtWidgets.QLabel(Marking)
        self.label_9.setGeometry(QtCore.QRect(160, 120, 161, 31))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(Marking)
        self.label_10.setGeometry(QtCore.QRect(20, 120, 111, 31))
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(Marking)
        self.label_11.setGeometry(QtCore.QRect(20, 140, 181, 31))
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(Marking)
        self.label_12.setGeometry(QtCore.QRect(20, 160, 191, 31))
        self.label_12.setObjectName("label_12")
        self.label_6 = QtWidgets.QLabel(Marking)
        self.label_6.setGeometry(QtCore.QRect(10, 200, 71, 16))
        self.label_6.setObjectName("label_6")
        self.label_13 = QtWidgets.QLabel(Marking)
        self.label_13.setGeometry(QtCore.QRect(20, 60, 301, 31))
        self.label_13.setObjectName("label_13")
        self.label_14 = QtWidgets.QLabel(Marking)
        self.label_14.setGeometry(QtCore.QRect(90, 100, 81, 31))
        self.label_14.setObjectName("label_14")

        self.retranslateUi(Marking)
        QtCore.QMetaObject.connectSlotsByName(Marking)

    def retranslateUi(self, Marking):
        _translate = QtCore.QCoreApplication.translate
        Marking.setWindowTitle(_translate("Marking", "MarkingSoftWare"))
        self.pushButton.setText(_translate("Marking", "??? ???"))
        self.Model.setItemText(0, _translate("Marking", "??????"))
        self.Model.setItemText(1, _translate("Marking", "??????"))
        self.Model.setItemText(2, _translate("Marking", "?????????"))
        self.label.setText(_translate("Marking", "????????????"))
        self.label_2.setText(_translate("Marking", "????????????"))
        self.label_3.setText(_translate("Marking", "????????????????????????????????????????????????????????????????????????"))
        self.label_4.setText(_translate("Marking", "???????????????"))
        self.label_5.setText(_translate("Marking", "Q ????????????"))
        self.label_7.setText(_translate("Marking", "A ????????????"))
        self.label_8.setText(_translate("Marking", "D ????????????"))
        self.label_9.setText(_translate("Marking", "S ????????????????????????????????????"))
        self.label_10.setText(_translate("Marking", "R ????????????????????????"))
        self.label_11.setText(_translate("Marking", "????????????????????? ??????????????????"))
        self.label_12.setText(_translate("Marking", "????????????????????? ?????????????????????"))
        self.label_6.setText(_translate("Marking", "??????????????????"))
        self.label_13.setText(_translate("Marking", "????????????????????????jpg???png????????????????????????XML?????????"))
        self.label_14.setText(_translate("Marking", "E ???????????????"))
