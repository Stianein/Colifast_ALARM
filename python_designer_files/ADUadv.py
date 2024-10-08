# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ADUadv.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(667, 551)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setStyleSheet("*{\n"
"    border: none;\n"
"    background-color: transparent;\n"
"    background: transparent;\n"
"    padding: 0;\n"
"    margin: 0;\n"
"    color: #000;\n"
"    font: 75 10pt \"Calibri\";\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"#centralwidget{\n"
"    background-color: #fff;\n"
"}\n"
"\n"
"\n"
"#QPushButton{\n"
"    text-align: left;\n"
"    padding: 2px, 10px;\n"
"}\n"
"\n"
"#frame_2{\n"
"    Background-color: #f3f4f5;\n"
"}\n"
"#frame_3, #adu_load, #reset_btn, #frame_4, #manual_command, #frame_6, #self_adu_button{\n"
"    background-color: #e0e0e0;\n"
"}\n"
"\n"
"#frame_5{\n"
"    Background-color: #f2f3f4;\n"
"}\n"
"\n"
"#reset_btn:hover , #adu_load:hover, #manual_command:hover, #self_adu_button:hover{\n"
"        background-color: #f2f3f4;\n"
"        /*box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.3);*/\n"
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
"QToolTip {\n"
"    color: black;\n"
"    background-color: #02a7a9;\n"
"}\n"
"QTextBrowser, QTextEdit{\n"
"    background-color: #fff;\n"
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
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.frame = QtWidgets.QFrame(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setContentsMargins(3, 7, 3, 7)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.aduImage = QtWidgets.QFrame(self.frame)
        self.aduImage.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.aduImage.setFrameShadow(QtWidgets.QFrame.Raised)
        self.aduImage.setObjectName("aduImage")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.aduImage)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout.addWidget(self.aduImage)
        self.frame_2 = QtWidgets.QFrame(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_2.sizePolicy().hasHeightForWidth())
        self.frame_2.setSizePolicy(sizePolicy)
        self.frame_2.setMaximumSize(QtCore.QSize(250, 16777215))
        self.frame_2.setStyleSheet("# Background-color: #f2f3f4;")
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout_2.setSpacing(10)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame_3 = QtWidgets.QFrame(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_3.sizePolicy().hasHeightForWidth())
        self.frame_3.setSizePolicy(sizePolicy)
        self.frame_3.setMaximumSize(QtCore.QSize(16777215, 120))
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_3)
        self.verticalLayout_3.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout_3.setSpacing(2)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.adu_load = QtWidgets.QPushButton(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.adu_load.sizePolicy().hasHeightForWidth())
        self.adu_load.setSizePolicy(sizePolicy)
        self.adu_load.setObjectName("adu_load")
        self.verticalLayout_3.addWidget(self.adu_load)
        self.reset_btn = QtWidgets.QPushButton(self.frame_3)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reset_btn.sizePolicy().hasHeightForWidth())
        self.reset_btn.setSizePolicy(sizePolicy)
        self.reset_btn.setObjectName("reset_btn")
        self.verticalLayout_3.addWidget(self.reset_btn)
        self.verticalLayout_2.addWidget(self.frame_3)
        self.frame_5 = QtWidgets.QFrame(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_5.sizePolicy().hasHeightForWidth())
        self.frame_5.setSizePolicy(sizePolicy)
        self.frame_5.setMaximumSize(QtCore.QSize(16777215, 150))
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.frame_5)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.status = QtWidgets.QLabel(self.frame_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.status.sizePolicy().hasHeightForWidth())
        self.status.setSizePolicy(sizePolicy)
        self.status.setMinimumSize(QtCore.QSize(0, 20))
        self.status.setMaximumSize(QtCore.QSize(16777215, 40))
        self.status.setObjectName("status")
        self.verticalLayout_7.addWidget(self.status)
        self.statusAdu = QtWidgets.QLineEdit(self.frame_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.statusAdu.sizePolicy().hasHeightForWidth())
        self.statusAdu.setSizePolicy(sizePolicy)
        self.statusAdu.setMaximumSize(QtCore.QSize(16777215, 30))
        self.statusAdu.setObjectName("statusAdu")
        self.verticalLayout_7.addWidget(self.statusAdu)
        self.verticalLayout_2.addWidget(self.frame_5)
        self.frame_6 = QtWidgets.QFrame(self.frame_2)
        self.frame_6.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame_6.sizePolicy().hasHeightForWidth())
        self.frame_6.setSizePolicy(sizePolicy)
        self.frame_6.setMinimumSize(QtCore.QSize(0, 0))
        self.frame_6.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_6)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.st_adu_txt = QtWidgets.QTextBrowser(self.frame_6)
        self.st_adu_txt.setMaximumSize(QtCore.QSize(16777215, 160))
        self.st_adu_txt.setObjectName("st_adu_txt")
        self.verticalLayout.addWidget(self.st_adu_txt, 0, QtCore.Qt.AlignTop)
        self.self_adu_button = QtWidgets.QPushButton(self.frame_6)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.self_adu_button.sizePolicy().hasHeightForWidth())
        self.self_adu_button.setSizePolicy(sizePolicy)
        self.self_adu_button.setMinimumSize(QtCore.QSize(0, 0))
        self.self_adu_button.setMaximumSize(QtCore.QSize(16777215, 54))
        self.self_adu_button.setObjectName("self_adu_button")
        self.verticalLayout.addWidget(self.self_adu_button)
        self.verticalLayout_2.addWidget(self.frame_6, 0, QtCore.Qt.AlignBottom)
        self.horizontalLayout.addWidget(self.frame_2)
        self.verticalLayout_5.addWidget(self.frame)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.adu_load.setText(_translate("Form", "ADU Load"))
        self.reset_btn.setText(_translate("Form", "Reset"))
        self.status.setText(_translate("Form", "Status"))
        self.st_adu_txt.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Calibri\'; font-size:10pt; font-weight:72; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'MS Shell Dlg 2\'; font-size:9pt; font-weight:400; color:#717171;\">SELF TEST: Run read and write tests to all inputs/outputs</span></p></body></html>"))
        self.self_adu_button.setText(_translate("Form", "TEST"))
