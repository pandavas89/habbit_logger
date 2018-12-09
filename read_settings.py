import os.path
import datetime
import sys
import shelve

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from common_settings import CommonSettings

class ReadSettings(CommonSettings):
    '''독서일기 설정 위젯'''
    def __init__(self, parent):
        super(ReadSettings, self).__init__(parent)

        self.setWindowTitle('[한쪽만] 설정')

        #출력 순서 데이터
        self.checker_list = ['linebreak', 'weeekday', 'autoVerify']
        self.text_list = ['header', 'comment', 'spreadsheet ID', 'nickname']

        self.setUI()
        self.mount()

    def setUI(self):
        '''UI를 설정한다'''
        self.addCategory('출력')
        self.addCheckerOption('항목 사이 칸 띄우기')
        self.addTextOption('헤더')
        self.addCheckerOption('요일 출력')
        self.addTextOption('감상')

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
        book_list = [['[Engineering Mathematics 9th], Kreyszig', 200, 220], ['[사람의 아들], 이문열', 120, 200]]
        for book in book_list:
            out_str += '%s %d ~ %d\n' %(book[0], book[1], book[2])
        record_list = [['누적 페이지 수', 100, 280], ['전공서적 읽기', 20, 180]]
        for record in record_list:
            out_str += '%s %d / %d\n' %(record[0], record[1], record[2])
        if self.checker[0].isChecked():
            out_str += '\n'
        comment_text = '짬을 내서 책을 읽은 것이 보람있는 하루였다.'
        out_str += '%s%s\n' %(self.text[1].text(), comment_text)

        self.preview_text.setText(out_str)
