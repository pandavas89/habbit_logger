import os.path
import datetime
import sys
import shelve

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class HabbitSettings(QTabWidget):
    '''개선일지 설정 위젯'''
    def __init__(self, settings, parent=None):
        super(HabbitSettings, self).__init__(parent)

        self.setWindowTitle('[내꺼하나+개선일지] 설정')

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

        label = self.setLabel('헤더')
        self.header = QLineEdit()
        self.header.setText(self.settings.value('header'))
        self.addWidget(label, 2)
        self.addWidget(self.header, 5, next=True)

        label = self.setLabel('요일 출력하기')
        self.weekday = QCheckBox()
        self.weekday.setChecked(self.settings.value('weekday'))
        self.addWidget(label, 6)
        self.addWidget(self.weekday, next=True)

        label = self.setLabel('기본습관')
        self.habbit = QLineEdit()
        self.habbit.setText(self.settings.value('habbit'))
        self.addWidget(label, 2)
        self.addWidget(self.habbit, 5, next=True)

        label = self.setLabel('개선일지')
        self.note = QLineEdit()
        self.note.setText(self.settings.value('note'))
        self.addWidget(label, 2)
        self.addWidget(self.note, 5, next=True)

        label = self.setLabel('항목 사이 칸 띄우기')
        self.linebreak = QCheckBox()
        self.linebreak.setChecked(self.settings.value('linebreak'))
        self.addWidget(label, 6)
        self.addWidget(self.linebreak, next=True)

        preview = QPushButton('미리보기')
        preview.clicked.connect(self.preview)
        save = QPushButton('저장')
        save.clicked.connect(self.saveSettings)
        self.addWidget(preview, 4)
        self.addWidget(save, 3, next=True)

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

    def preview(self):
        '''미리보기 창을 띄운다'''
        out_str = self.settings.value('header')
        out_str += '1 %s' %datetime.date.today().strftime('%y%m%d')
        if self.settings.value('weekday'):
            out_str += ' 월'
        out_str +='\n'
        if self.settings.value('linebreak'):
            out_str += '\n'
        out_str += '%s\n' %self.settings.value('habbit')
        out_str += '디지털 습관 : 1 / 2\n'
        out_str += '아날로그 습관 : 13.1 / 182.1\n'
        if self.settings.value('linebreak'):
            out_str += '\n'
        out_str += '%s\n' %self.settings.value('note')
        out_str += '3. 코딩을 열심히 했다'

        msg = QMessageBox()
        msg.setWindowTitle('미리보기')
        msg.setText(out_str)
        msg.exec_()

    def saveSettings(self):
        self.settings.setValue('header', self.header.text())
        self.settings.setValue('habbit', self.habbit.text())
        self.settings.setValue('note', self.note.text())
        self.settings.setValue('linebreak', int(self.linebreak.isChecked()))
        self.settings.setValue('weekday', int(self.weekday.isChecked()))

    def setLabel(self, label_name):
        '''지정된 양식의 QLabel 객체를 리턴한다'''
        label = QLabel(label_name)
        label.setAlignment(Qt.AlignCenter)
        label.setFrameShape(QFrame.Panel)
        return label

    def addWidget(self, t_widget, width=1, next=False):
        self.grid[-1].addWidget(t_widget, self.row_count, self.col_count, 1, width)
        if next:
            self.row_count += 1
            self.col_count = 0
        else:
            self.col_count += width
