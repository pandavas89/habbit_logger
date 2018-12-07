import os.path
import datetime
import sys
import shelve

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class DietSettings(QTabWidget):
    '''식단일기 설정 위젯'''
    def __init__(self, settings, parent=None):
        super(DietSettings, self).__init__(parent)

        self.setWindowTitle('[먹은거] 설정')

        self.settings = settings
        self.tab = []
        self.grid = []
        self.setUI()

    def setUI(self):
        '''UI를 설정한다'''
        #출력설정
        tab_order = 0

        self.row_count = 0
        self.col_count = 0
        self.tab.append(QWidget())
        tab = self.tab[-1]
        self.grid.append(QGridLayout())
        self.setTabText(tab_order, '출력')
        tab.setLayout(self.grid[tab_order])
        self.addTab(self.tab[tab_order], '출력')

        label = QLabel('헤더')
        self.header = QLineEdit()
        self.header.setText(self.settings.value('header'))
        self.addWidget(label, 2)
        self.addWidget(self.header, 5, next=True)

        label = QLabel('요일 출력하기')
        self.weekday = QCheckBox()
        self.weekday.setChecked(self.settings.value('weekday'))
        self.addWidget(label, 6)
        self.addWidget(self.weekday, next=True)

        label =QLabel('항목 사이 칸 띄우기')
        self.linebreak = QCheckBox()
        self.linebreak.setChecked(self.settings.value('linebreak'))
        self.addWidget(label, 6)
        self.addWidget(self.linebreak, next=True)

        label = QLabel('목표')
        self.goal = QLineEdit()
        self.goal.setText(self.settings.value('goal'))
        self.addWidget(label, 3)
        self.addWidget(self.goal, 4, next=True)

        label = QLabel('활동')
        self.action = QLineEdit()
        self.action.setText(self.settings.value('action'))
        self.addWidget(label, 3)
        self.addWidget(self.action, 4, next=True)

        label = QLabel('식단')
        self.meal = QLineEdit()
        self.meal.setText(self.settings.value('meal'))
        self.addWidget(label, 3)
        self.addWidget(self.meal, 4, next=True)

        label2 = QLabel('칼로리 추적')
        self.calory = QCheckBox()
        self.calory.setChecked(self.settings.value('calory'))
        self.addWidget(label2, 6)
        self.addWidget(self.calory, next=True)

        label = QLabel('잘한일')
        self.deed = QLineEdit()
        self.deed.setText(self.settings.value('deed'))
        self.addWidget(label, 3)
        self.addWidget(self.deed, 4, next=True)

        save_button = QPushButton('저장')
        save_button.clicked.connect(self.saveSettings)
        preview_button = QPushButton('미리보기')
        preview_button.clicked.connect(self.preview)
        self.addWidget(save_button, 3)
        self.addWidget(preview_button, 4)

        #자동인증 옵션
        tab_order += 1

        self.row_count = 0
        self.col_count = 0
        self.tab.append(QWidget())
        tab = self.tab[-1]
        self.grid.append(QGridLayout())
        self.setTabText(tab_order, '자동인증')
        tab.setLayout(self.grid[tab_order])
        self.addTab(self.tab[tab_order], '자동인증')

        switch_label = QLabel('자동인증 활성화')
        self.autoVerify = QCheckBox()
        if self.settings.value('autoVerify'):
            self.autoVerify.setChecked(self.settings.value('autoVerify'))
        self.addWidget(switch_label)
        self.addWidget(self.autoVerify, next=True)

        sheetID = QLabel('spreadsheet ID')
        self.sheetID = QLineEdit()
        if self.settings.value('sheetID'):
            self.sheetID.setText(self.settings.value('sheetID'))
        self.addWidget(sheetID)
        self.addWidget(self.sheetID, next=True)

        nickname = QLabel('별명')
        self.nickname = QLineEdit()
        if self.settings.value('nickname'):
            self.nickname.setText(self.settings.value('nickname'))
        self.addWidget(nickname)
        self.addWidget(self.nickname, next=True)

        auto_save = QPushButton('저장')
        auto_save.clicked.connect(self.autoSave)
        self.addWidget(auto_save, 2)

    def autoSave(self):
        self.settings.setValue('autoVerify', int(self.autoVerify.isChecked()))
        self.settings.setValue('sheetID', self.sheetID.text())
        self.settings.setValue('nickname', self.nickname.text())

    def setLabel(self, label_name):
        '''지정된 양식의 QLabel 객체를 리턴한다'''
        label = QLabel(label_name)
        label.setAlignment(Qt.AlignCenter)
        label.setFrameShape(QFrame.Panel)
        return label

    def saveSettings(self):
        self.settings.setValue('header', self.header.text())
        self.settings.setValue('goal', self.goal.text())
        self.settings.setValue('action', self.action.text())
        self.settings.setValue('meal', self.meal.text())
        self.settings.setValue('deed', self.deed.text())
        self.settings.setValue('weekday', int(self.weekday.isChecked()))
        self.settings.setValue('linebreak', int(self.linebreak.isChecked()))
        self.settings.setValue('calory', int(self.calory.isChecked()))

    def addWidget(self, t_widget, width=1, next=False):
        self.grid[-1].addWidget(t_widget, self.row_count, self.col_count, 1, width)
        if next:
            self.row_count += 1
            self.col_count = 0
        else:
            self.col_count += width

    def preview(self):
        pass
