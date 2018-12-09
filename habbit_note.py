import os.path
import datetime
import sys
import shelve

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from common_note import CommonNote
from habbit_data import HabbitLog
from habbit_settings import HabbitSettings

class HabbitNote(CommonNote):
    '''습관+개선일지 프로그램'''
    def __init__(self, parent=None):
        '''기초적인 내용을 설정한다'''
        super(HabbitNote, self).__init__(parent)
        self.log = HabbitLog()
        self.version = 40
        self.log_name = 'h_log'

        #테스트용
        '''
        self.log.b_date = datetime.date(year=2018, month=12, day=1)
        self.log.habbit = [['d','독서', 2], ['a', '러닝', 16.7]]
        self.log.counter = 17
        '''

        #설정을 적용한다.
        self.settings = QSettings('pandavas', 'HabbitNote')
        if not(self.settings.value('init')):
            self.settings.setValue('init', 1)
            self.settings.setValue('header', '[내꺼하나+개선일지] D+')
            self.settings.setValue('habbit', '기본습관')
            self.settings.setValue('note', '개선일지')
            self.settings.setValue('linebreak', 1)
            self.settings.setValue('weekday', 1)
            self.settings.setValue('autoVerify', 0)

        self.num_log = 1

        self.setWindowTitle('[내꺼하나+개선일지] v%0.2f' %(self.version/100))

        self.load()
        self.setUI()
        self.mount()

    def setUI(self):
        '''UI를 설정한다'''
        #d-day
        self.addDdayCounter()

        #습관
        self.addCategory('습관')
        h_add_button = QPushButton('추가')
        h_add_button.clicked.connect(self.addHabbit)
        h_del_button = QPushButton('제거')
        h_del_button.clicked.connect(self.delHabbit)
        self.addWidget(h_add_button)
        self.addWidget(h_del_button, next=True)

        #습관 리스트
        self.order = []
        if len(self.log.habbit) > 0:
            for habbit in self.log.habbit:
                self.order.append(habbit[0])
                if habbit[0] > 'b':
                    self.addDigitalCounter(habbit[1])
                    self.c_value.append(habbit[2])
                else:
                    self.addAnalogCounter(habbit[1])
                    self.c_value.append(habbit[2])

        #개선일지
        self.addCategory('개선일지')
        l_add_button = QPushButton('추가')
        l_add_button.clicked.connect(self.addLogBtn)
        l_del_button = QPushButton('제거')
        l_del_button.clicked.connect(self.delLogBtn)
        self.addWidget(l_add_button)
        self.addWidget(l_del_button, next=True)

        for i in range(self.num_log):
            self.addLog()

        self.mount()

    def mount(self):
        '''self.log의 데이터를 어플리케이션에 반영한다'''
        self.b_date.setDate(self.log.date)
        for habbit in self.log.habbit:
            idx = self.log.habbit.index(habbit)
            self.name[idx].setText(habbit[1])
            self.counter[idx].setValue(habbit[2])
        self.log_counter[0].setValue(self.log.counter)

    def addHabbit(self):
        '''습관을 추가한다'''
        #습관 종류 선택
        message = QMessageBox()
        message.setWindowTitle('습관 추가')
        message.addButton(QPushButton('디지털'), QMessageBox.YesRole)
        message.addButton(QPushButton('아날로그'), QMessageBox.NoRole)
        message.addButton(QPushButton('취소'), QMessageBox.RejectRole)
        ok = message.exec_()

        #취소가 아닐 때
        if ok < 2:
            #연속 습관 추가
            if ok > 0:
                self.log.habbit.append(['a', '', 0])
            else:
                self.log.habbit.append(['d', '', 0])
            self.clear()
            self.setUI()

    def delHabbit(self):
        '''습관을 제거한다'''
        message = QMessageBox()
        message.setWindowTitle('습관 제거')
        message.setText('습관 : %s 제거됩니다.' %self.name[-1].text())
        message.addButton(QPushButton('예'), QMessageBox.YesRole)
        message.addButton(QPushButton('아니오'), QMessageBox.NoRole)
        ok = message.exec_()
        if ok < 1:
            self.log.habbit.pop()
            self.clear()
            self.setUI()
            self.mount()

    def addLogBtn(self):
        '''개선일지를 추가한다'''
        self.num_log += 1
        self.clear()
        self.setUI()
        self.mount()

    def delLogBtn(self):
        '''마지막 개선일지를 삭제한다'''
        if self.num_log > 1:
            self.num_log -= 1
            self.clear()
            self.setUI()
            self.mount()
        else:
            message = QMessageBox()
            message.setWindowTitle('오류')
            message.setText('마지막 개선일지는 삭제할 수 없습니다')
            message.exec_()

    def save(self, export=False):
        '''저장한다'''
        self.log.date = self.b_date.date()
        habbit_list = []
        for habbit in self.name:
            idx = self.name.index(habbit)
            habbit_list.append([self.order[idx], habbit.text(), self.counter[idx].value()])
        self.log.habbit = habbit_list
        if export:
            self.log.counter = self.log_counter[-1].value() + 1
        else:
            self.log.counter = self.log_counter[-1].value()

        super(HabbitNote, self).save()

    def export(self):
        '''기록을 출력한다'''
        date = self.c_date.date().toString('yyMMdd')
        out_str = self.settings.value('header')
        d_day = self.b_date.date().daysTo(self.c_date.date()) + 1
        out_str += '%s, %s '%(d_day, date)
        wdays = '월화수목금토일'
        if self.settings.value('weekday'):
            out_str += wdays[self.c_date.date().toPyDate().weekday()] + '\n'
        else:
            out_str += '\n'
        if self.settings.value('linebreak'):
            out_str += '\n'
        out_str += self.settings.value('habbit') + '\n'
        for habbit in self.name:
            idx = self.name.index(habbit)
            #아날로그 습관일 때
            if self.order[idx] < 'b':
                out_str += '%s : %0.1f / %0.1f\n' %(habbit.text(), self.checker[idx].value(), self.counter[idx].value())
            #디지털 습관일 때
            else:
                out_str += '%s : %d / %d\n' %(habbit.text(), self.checker[idx].isChecked(), self.counter[idx].value())
        if self.settings.value('linebreak'):
            out_str += '\n'
        out_str += self.settings.value('note') + '\n'
        for log in self.log_text:
            idx = self.log_text.index(log)
            out_str += '%d. %s\n' %(self.log_counter[idx].value(), log.text())

        self.exportMessage(out_str, '오늘의 개선일지')

    def showSettings(self):
        self.setting_widget = HabbitSettings(self)
        self.setting_widget.show()

if __name__ == '__main__':
    application = QApplication(sys.argv)
    main_widget = HabbitNote()
    main_widget.show()
    sys.exit(application.exec_())
