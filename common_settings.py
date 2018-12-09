import os.path
import datetime
import sys
import shelve

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class CommonSettings(QMainWindow):
    '''공통 설정 위젯'''
    def __init__(self, parent):
        self.parent = parent
        self.settings = self.parent.settings

        super(CommonSettings, self).__init__(parent)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        total_layout = QHBoxLayout()
        main_widget.setLayout(total_layout)
        self.stack = QVBoxLayout()
        total_layout.addLayout(self.stack)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        total_layout.addWidget(self.preview_text)
        self.widget_row = QHBoxLayout()

        self.checker = []
        self.text = []
        self.counter = []

    def addCategory(self, category_name):
        '''그룹 박스를 추가한다'''
        self.groupbox = QGroupBox(category_name)
        self.groupbox.setStyleSheet("QGroupBox { font=wdight: bold; font-size: 12pt; border: 1px solid black; border-radius: 5px; padding: 10px;}")
        self.groupbox.setAlignment(Qt.AlignCenter)
        self.group_vbox = QVBoxLayout()
        self.groupbox.setLayout(self.group_vbox)
        self.stack.addWidget(self.groupbox)

    def addWidget(self, t_widget, next=False):
        '''전달받은 위젯을 추가한다'''
        self.widget_row.addWidget(t_widget)
        if next:
            self.group_vbox.addLayout(self.widget_row)
            self.widget_row = QHBoxLayout()

    def addCheckerOption(self, name):
        '''체크 옵션을 추가한다'''
        label = QLabel(name)
        self.checker.append(QCheckBox())
        self.checker[-1].setFixedWidth(18)
        self.checker[-1].stateChanged.connect(self.update)
        self.addWidget(label)
        self.addWidget(self.checker[-1], next=True)

    def addTextOption(self, name):
        '''텍스트 옵션을 추가한다'''
        label = QLabel(name)
        self.text.append(QLineEdit())
        self.text[-1].textChanged.connect(self.update)
        self.addWidget(label)
        self.addWidget(self.text[-1], next=True)

    def addValueOption(self, name):
        '''수치 옵션을 추가한다'''
        label = QLabel(name)
        self.counter.append(QSpinBox())
        self.counter[-1].valueChange(self.update)
        self.addWidget(label)
        self.addWidget(self.ounter[-1], next=True)

    def addButtons(self):
        '''저장/미리보기 버튼을 추가한다'''
        save_button = QPushButton('저장')
        save_button.clicked.connect(self.save)
        self.stack.addWidget(save_button)

    def mount(self):
        '''설정값을 화면에 반영한다'''
        for checker in self.checker:
            idx = self.checker.index(checker)
            if self.settings.value(self.checker_list[idx]) is None:
                self.settings.setValue(self.checker_list[idx], 0)
            checker.setChecked(int(self.settings.value(self.checker_list[idx])))
        for text in self.text:
            idx = self.text.index(text)
            text.setText(self.settings.value(self.text_list[idx]))

    def save(self):
        '''설정값을 저장한다'''
        for checker in self.checker:
            idx = self.checker.index(checker)
            self.settings.setValue(self.checker_list[idx], int(checker.isChecked()))
        for text in self.text:
            idx = self.text.index(text)
            self.settings.setValue(self.text_list[idx], text.text())
