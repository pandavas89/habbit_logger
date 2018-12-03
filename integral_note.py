import os.path
import datetime
import sys
import shelve

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import habbit_note
import diet_note
import read_note

'''
통합 습관노트 어플리케이션
1. updater4pyi를 이용한 어플리케이션 자동 업데이트
2. 보안 강화
3. 자동 인증기능 추가
'''

class integral_note(QMainWindow):
    '''통합 습관노트 어플리케이션'''
    def __init__(self, parent=None):
        #저장 파일 이름
        super(integral_note, self).__init__(parent)
        self.db_name = 'integral_note.db'
        self.version = 2

        self.setWindowTitle('Integral Note v_%0.1f' %(self.version/10))
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.grid = QGridLayout()
        main_widget.setLayout(self.grid)
        self.setUI()

    def setUI(self):
        '''UI를 설정한다'''
        h_btn = self.setButton('내꺼하나+개선일지')
        h_btn.clicked.connect(self.habbitShow)
        d_btn = self.setButton('먹은거')
        d_btn.clicked.connect(self.dietShow)
        r_btn = self.setButton('한쪽만')
        r_btn.clicked.connect(self.readShow)
        self.grid.addWidget(h_btn, 0, 0)
        self.grid.addWidget(d_btn, 1, 0)
        self.grid.addWidget(r_btn, 2, 0)

    def setButton(self, btn_name, font_size=20, padding=12):
        '''정해진 스타일의 버튼을 리턴한다'''
        font = QFont()
        font.setPointSize(font_size)
        button = QPushButton(btn_name)
        button.setFont(font)
        button.setStyleSheet("padding: %dpx;" %padding)
        return button

    def habbitShow(self):
        self.h_widget = habbit_note.HabbitNote(self.db_name)
        self.h_widget.show()

    def dietShow(self):
        self.d_widget = diet_note.DietNote(self.db_name)
        self.d_widget.show()

    def readShow(self):
        self.r_widget = read_note.ReadNote(self.db_name)
        self.r_widget.show()


if __name__=='__main__':
    application = QApplication(sys.argv)
    main_widget = integral_note()
    main_widget.show()
    sys.exit(application.exec_())
