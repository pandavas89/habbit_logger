import os.path
import datetime
import sys
import shelve

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from common_note import CommonNote
from read_data import ReadLog
from read_settings import ReadSettings

class ReadNote(CommonNote):
    '''독서일기 프로그램'''
    def __init__(self, parent=None):
        super(ReadNote, self).__init__(parent)
        self.log = ReadLog()
        self.version = 40
        self.log_name = 'r_log'

        #테스트용
        '''
        self.log.date = datetime.date(year=2018, month=12, day=1)
        self.log.c_book = [['체 게바라 평전', 100, 892],['나를 운디드니에 묻어주오', 227, 680]]
        self.log.record = [['누적 읽은 페이지수', 1200], ['소설 읽기', 500]]
        '''

        #설정을 적용한다.
        self.settings = QSettings('pandavas', 'ReadNote')
        if not(self.settings.value('init')):
            self.settings.setValue('init', 1)
            self.settings.setValue('header', '[한쪽만]#DAY_')
            self.settings.setValue('comment', '오늘의 감상 : ')
            self.settings.setValue('linebreak', 1)
            self.settings.setValue('weekday', 1)
            self.settings.setValue('autoVerify', 0)

        self.setWindowTitle('[한쪽만] v_%0.2f' %(self.version/100))

        self.load()
        self.setUI()
        self.mount()

    def setUI(self):
        '''UI를 설정한다'''
        #d-day
        self.addDdayCounter()

        #현재도서
        self.addCategory('현재 도서')
        b_add_button = QPushButton('추가')
        b_add_button.clicked.connect(self.addBook)
        b_del_button = QPushButton('삭제')
        b_del_button.clicked.connect(self.delBook)
        self.addWidget(b_add_button)
        self.addWidget(b_del_button, next=True)
        if len(self.log.c_book) > 0:
            for book in self.log.c_book:
                self.addPageCounter(book[0])
                self.c_value.append(book[1])

        #기록
        self.addCategory('기록')
        r_add_button = QPushButton('추가')
        r_add_button.clicked.connect(self.addRecord)
        r_del_button = QPushButton('삭제')
        r_del_button.clicked.connect(self.delRecord)

        self.addWidget(r_add_button)
        self.addWidget(r_del_button, next=True)
        if len(self.log.record) > 0:
            for record in self.log.record:
                self.addAnalogCounter(record[0], point=False)

        #감상
        self.addCategory('감상')
        self.comment = QTextEdit()
        self.addWidget(self.comment, next=True)

    def addBook(self):
        '''도서를 추가한다'''
        self.log.c_book.append(['', 0, 0])
        self.clear()
        self.setUI()
        self.mount()

    def delBook(self):
        '''도서를 삭제한다'''
        if len(self.log.c_book) > 0:
            self.log.c_book.pop()
            self.clear()
            self.setUI()
            self.mount()

    def addRecord(self):
        '''기록을 추가한다'''
        self.log.record.append(['', 0])
        self.clear()
        self.setUI()
        self.mount()

    def delRecord(self):
        '''기록을 삭제한다'''
        if len(self.log.record) > 0:
            message = QMessageBox()
            message.setWindowTitle('습관 제거')
            message.setText('습관 : %s 제거됩니다.' %self.name[-1].text())
            message.addButton(QPushButton('예'), QMessageBox.YesRole)
            message.addButton(QPushButton('아니오'), QMessageBox.NoRole)
            ok = message.exec_()
            if ok < 1:
                self.log.record.pop()
                self.clear()
                self.setUI()
                self.mount()

    def save(self, export=False):
        '''self.log의 정보를 저장한다'''
        self.log.date = self.b_date.date()

        book_list = []
        if len(self.b_name) > 0:
            for book in self.b_name:
                idx = self.b_name.index(book)
                book_list.append([book.text(), self.b_end[idx].value(), self.b_total[idx].value()])
        self.log.c_book = book_list

        record_list = []
        if len(self.name) > 0:
            for record in self.name:
                idx = self.name.index(record)
                record_list.append([record.text(), self.counter[idx].value()])
        self.log.record = record_list

        super(ReadNote, self).save()

    def mount(self):
        '''self.log의 데이터를 어플리케이션에 반영한다'''
        self.b_date.setDate(self.log.date)

        for book in self.log.c_book:
            idx = self.log.c_book.index(book)
            self.b_name[idx].setText(book[0])
            self.b_start[idx].setValue(book[1])
            self.b_total[idx].setValue(book[2])
            self.b_end[idx].setValue(book[1])

        for record in self.log.record:
            idx = self.log.record.index(record)
            self.name[idx].setText(record[0])
            self.counter[idx].setValue(record[1])

    def export(self):
        '''기록을 출력한다'''
        date = self.c_date.date().toString('yyMMdd')
        out_str = self.settings.value('header')
        out_str += '%s %s' %(self.d_day.text(), date)
        if self.settings.value('weekday'):
            wdays = '월화수목금토일'
            out_str += wdays[self.c_date.date().toPyDate().weekday()] + '\n'
        else:
            out_str += '\n'
        if self.settings.value('linebreak'):
            out_str += '\n'
        out_str += '%s %d~%d\n' %(self.b_name.text(), self.b_start.value(), self.b_total.value())
        if self.settings.value('linebreak'):
            out_str += '\n'
        if len(self.log.record) > 0:
            for record in self.name:
                idx = self.name.index(record)
                out_str += '%s : %d / %d\n' %(record.text(), self.checker[idx].value(), self.counter[idx].value())
        out_str += self.settings.value('comment')
        out_str += self.comment.toPlainText()

        self.exportMessage(out_str, '오늘의 독서일기')

    def showSettings(self):
        self.setting_widget = ReadSettings(self)
        self.setting_widget.show()


if __name__ == '__main__':
    application = QApplication(sys.argv)
    main_widget = ReadNote()
    main_widget.show()
    sys.exit(application.exec_())
