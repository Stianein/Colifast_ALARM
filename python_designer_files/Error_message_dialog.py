# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Error_message_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(681, 448)
        Dialog.setStyleSheet("*{\n"
"    border: none;\n"
"    background-color: transparent;\n"
"    background: transparent;\n"
"    padding: 0;\n"
"    margin: 0;\n"
"    color: #000;\n"
"    font: 75 10pt \"Calibri\";\n"
"    border-radius: 4px;\n"
"\n"
"}\n"
"\n"
"#centralWidget{\n"
"    background-color: #fafafa;\n"
"}\n"
"\n"
"#frame_5, #frame_6, #frame, #acceptFrame{\n"
"    background-color: #f4f4f4;\n"
"}\n"
"\n"
"QMenu::item:selected {\n"
"    background-color: white;\n"
"    color: white;\n"
"}\n"
"QComboBox::item:selected{\n"
"    background-color: white;\n"
"    color: white;\n"
"}\n"
"QComboBox QAbstractItemView  {\n"
"    background-color: white;\n"
"}\n"
"\n"
"QPushButton {\n"
"        border: none;\n"
"        padding: 10px;\n"
"        background-color: #f4f4f4;\n"
"        color: black;\n"
"        border-radius: 5px;\n"
"       /* box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3);*/\n"
"    }\n"
"    QPushButton:hover {\n"
"        background-color: #e0e0e0;\n"
"        /*box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.3);*/\n"
"    }\n"
"    QPushButton:pressed {\n"
"        background-color: #d4d4d4;\n"
"        /*box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.3);*/\n"
"    }")
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.centralWidget = QtWidgets.QWidget(Dialog)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.headerContainer = QtWidgets.QWidget(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.headerContainer.sizePolicy().hasHeightForWidth())
        self.headerContainer.setSizePolicy(sizePolicy)
        self.headerContainer.setObjectName("headerContainer")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.headerContainer)
        self.horizontalLayout_4.setContentsMargins(4, 4, 4, 4)
        self.horizontalLayout_4.setSpacing(4)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.frame_5 = QtWidgets.QFrame(self.headerContainer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_5.sizePolicy().hasHeightForWidth())
        self.frame_5.setSizePolicy(sizePolicy)
        self.frame_5.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_11 = QtWidgets.QLabel(self.frame_5)
        self.label_11.setMinimumSize(QtCore.QSize(50, 5))
        self.label_11.setText("")
        self.label_11.setPixmap(QtGui.QPixmap(":/images/Images/Colifast_50pix_medium.png"))
        self.label_11.setScaledContents(False)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_7.addWidget(self.label_11, 0, QtCore.Qt.AlignHCenter)
        self.horizontalLayout_4.addWidget(self.frame_5)
        self.frame_6 = QtWidgets.QFrame(self.headerContainer)
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_6)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.minimizebtn = QtWidgets.QPushButton(self.frame_6)
        self.minimizebtn.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/icons/minus.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.minimizebtn.setIcon(icon)
        self.minimizebtn.setObjectName("minimizebtn")
        self.horizontalLayout_5.addWidget(self.minimizebtn)
        self.closebtn = QtWidgets.QPushButton(self.frame_6)
        self.closebtn.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/icons/x.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.closebtn.setIcon(icon1)
        self.closebtn.setIconSize(QtCore.QSize(16, 16))
        self.closebtn.setObjectName("closebtn")
        self.horizontalLayout_5.addWidget(self.closebtn)
        self.horizontalLayout_4.addWidget(self.frame_6, 0, QtCore.Qt.AlignRight)
        self.verticalLayout_2.addWidget(self.headerContainer, 0, QtCore.Qt.AlignTop)
        self.mainBodyContainer = QtWidgets.QWidget(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainBodyContainer.sizePolicy().hasHeightForWidth())
        self.mainBodyContainer.setSizePolicy(sizePolicy)
        self.mainBodyContainer.setObjectName("mainBodyContainer")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.mainBodyContainer)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame = QtWidgets.QFrame(self.mainBodyContainer)
        self.frame.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_4.setContentsMargins(20, 20, 20, 0)
        self.verticalLayout_4.setSpacing(20)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.errorLabel = QtWidgets.QLabel(self.frame)
        self.errorLabel.setObjectName("errorLabel")
        self.verticalLayout_4.addWidget(self.errorLabel, 0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.verticalLayout_3.addWidget(self.frame)
        self.customFrame = QtWidgets.QFrame(self.mainBodyContainer)
        self.customFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.customFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.customFrame.setObjectName("customFrame")
        self.bottleSize = QtWidgets.QSpinBox(self.customFrame)
        self.bottleSize.setGeometry(QtCore.QRect(9, 27, 35, 34))
        self.bottleSize.setMinimumSize(QtCore.QSize(0, 34))
        self.bottleSize.setSingleStep(7)
        self.bottleSize.setObjectName("bottleSize")
        self.frameMethod = QtWidgets.QFrame(self.customFrame)
        self.frameMethod.setGeometry(QtCore.QRect(210, 0, 121, 56))
        self.frameMethod.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameMethod.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameMethod.setObjectName("frameMethod")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.frameMethod)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.methodFile = QtWidgets.QLabel(self.frameMethod)
        self.methodFile.setObjectName("methodFile")
        self.verticalLayout_5.addWidget(self.methodFile)
        self.methodSelector = QtWidgets.QComboBox(self.frameMethod)
        self.methodSelector.setEnabled(True)
        self.methodSelector.setStyleSheet("")
        self.methodSelector.setObjectName("methodSelector")
        self.methodSelector.addItem("")
        self.verticalLayout_5.addWidget(self.methodSelector)
        self.verticalLayout_3.addWidget(self.customFrame)
        self.acceptFrame = QtWidgets.QFrame(self.mainBodyContainer)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.acceptFrame.sizePolicy().hasHeightForWidth())
        self.acceptFrame.setSizePolicy(sizePolicy)
        self.acceptFrame.setMaximumSize(QtCore.QSize(16777215, 70))
        self.acceptFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.acceptFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.acceptFrame.setObjectName("acceptFrame")
        self.verticalLayout_3.addWidget(self.acceptFrame)
        self.verticalLayout_2.addWidget(self.mainBodyContainer)
        self.verticalLayout.addWidget(self.centralWidget)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.minimizebtn.setToolTip(_translate("Dialog", "Minimize Window"))
        self.closebtn.setToolTip(_translate("Dialog", "Close Window"))
        self.errorLabel.setText(_translate("Dialog", "TextLabel"))
        self.methodFile.setText(_translate("Dialog", "Method File"))
        self.methodSelector.setItemText(0, _translate("Dialog", "test"))
import Icons_rc