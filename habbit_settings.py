import os.path
import datetime
import sys
import shelve

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from common_settings import CommonSettings

class HabbitSettings(CommonSettings):
    '''식단일기 설정 위젯'''
    def __init__(self, parent):
        super(HabbitSettings, self).__init__(parent)

        self.setWindowTitle('[내꺼하나] 설정')

        #출력 순서 데이터
        self.checker_list = ['linebreak', 'weekday', 'autoVerify']
        self.text_list = ['header', 'habbit', 'note', 'spreadsheet ID', 'nickname']


        self.setUI()
        self.mount()

    def setUI(self):
        '''UI를 설정한다'''

        self.addCategory('출력')
        self.addCheckerOption('항목 사이 칸 띄우기')
        self.addTextOption('헤더')
        self.addCheckerOption('요일 출력')
        self.addTextOption('기본습관')
        self.addTextOption('개선일지')

        self.addCategory('자동인증')
        self.addCheckerOption('자동인증 사용')
        self.addTextOption('spreadsheet ID')
        self.addTextOption('별명')

        self.addButtons()

    def update(self):
        '''미리보기를 업데이트한다'''
        date = datetime.date(year=2018, month=1, day=1)
        out_str = self.text[0].text()
        d_day = datetime.date.today() - date + datetime.timedelta(days=1)
        date = date.strftime('%y%m%d')
        d_day = d_day.days
        out_str += '%s %s ' %(d_day, date)
        if self.checker[1].isChecked():
            wdays = '월화수목금토일'
            out_str += wdays[datetime.date.today().weekday()]
        out_str += '\n'
        if self.checker[0].isChecked():
            out_str += '\n'
        out_str += '%s\n' %(self.text[1].text())
        action_list = [['d', '운동', 1, 7], ['a', '독서', 10, 220]]
        for action in action_list:
            idx = action_list.index(action)
            out_str += '%s : %d / %d\n' %(action[1], action[2], action[3])
        if self.checker[0].isChecked():
            out_str += '\n'
        out_str += '\n'
        out_str += self.text[2].text() + '\n'
        deed_list = [[16, '배가 고팠지만 간식을 잘 참았다.']]
        for deed in deed_list:
            out_str += '%d. %s\n' %(deed[0], deed[1])

        self.preview_text.setText(out_str)
