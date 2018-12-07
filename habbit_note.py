import os.path
import datetime
import sys
import shelve

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import habbit_settings
import INote_gdapi

class HabbitNote(QMainWindow):
    '''개선일지 위젯'''
    def __init__(self, db_name, parent=None):
        '''기초적인 내용을 설정한다'''
        super(HabbitNote, self).__init__(parent)
        self.db_name = db_name
        self.version = 3
        self.d_version = 2

        self.settings = QSettings('pandavas', 'HabbitNote')
        if not(self.settings.value('init')):
            self.settings.setValue('init', 1)
            self.settings.setValue('header', '[내꺼하나+개선일지] D+')
            self.settings.setValue('habbit', '기본습관')
            self.settings.setValue('note', '개선일지')
            self.settings.setValue('linebreak', 1)
            self.settings.setValue('weekday', 1)
            self.settings.setValue('autoVerify', 0)

        self.hLog = HabbitLog()

        self.setWindowTitle('[내꺼하나+개선일지] v_%0.1f' %(self.version/10))

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.grid = QGridLayout()
        main_widget.setLayout(self.grid)

        self.num_log = 1

        self.load()
        self.setUI()
        self.mount()

    def setUI(self):
        '''UI를 설정한다'''
        self.row_count = 0
        self.col_count = 0

        #시작일자, 현재일자 및 D+ 카운터
        self.b_date = QDateEdit()
        self.b_date.dateChanged.connect(self.d_day_update)
        self.c_date = QDateEdit()
        self.c_date.dateChanged.connect(self.d_day_update)
        self.d_day = QLabel('')
        self.d_day.setAlignment(Qt.AlignCenter)
        self.c_date.setDate(datetime.date.today())
        setting_button = QPushButton('설정')
        setting_button.clicked.connect(self.showSettings)
        self.addWidget(self.b_date)
        self.addWidget(self.c_date)
        self.addWidget(self.d_day)
        self.addWidget(setting_button, next=True)

        #습관 헤더
        habbit_label = self.setLabel('습관')
        h_add_button = QPushButton('추가')
        h_add_button.clicked.connect(self.addHabbit)
        h_del_button = QPushButton('삭제')
        h_del_button.clicked.connect(self.delHabbit)
        self.addWidget(habbit_label, 2)
        self.addWidget(h_add_button)
        self.addWidget(h_del_button, next=True)

        #습관
        self.h_order = []
        self.h_name = []
        self.h_check = []
        self.h_count = []
        if len(self.hLog.habbit) > 0:
            for habbit in self.hLog.habbit:
                #아날로그 카운터일 때
                if habbit[0] < 'b':
                    self.h_order.append('a')
                    self.h_check.append(QDoubleSpinBox())
                    self.h_check[-1].setMaximum(9999)
                    self.h_check[-1].valueChanged.connect(self.hUpdate)
                    self.h_count.append(QDoubleSpinBox())
                    self.h_count[-1].setMaximum(999999)
                #디지털 카운터일 때
                else:
                    self.h_order.append('d')
                    self.h_check.append(QCheckBox())
                    self.h_check[-1].stateChanged.connect(self.hUpdate)
                    self.h_count.append(QSpinBox())
                    self.h_count[-1].setMaximum(999999)
                self.h_name.append(QLineEdit())
                self.addWidget(self.h_name[-1], 2)
                self.addWidget(self.h_check[-1])
                self.addWidget(self.h_count[-1], next=True)

        #개선일지 헤더
        log_label = self.setLabel('개선일지')
        l_add_button = QPushButton('추가')
        l_add_button.clicked.connect(self.addLog)
        l_del_button = QPushButton('삭제')
        l_del_button.clicked.connect(self.delLog)
        self.addWidget(log_label, 2)
        self.addWidget(l_add_button)
        self.addWidget(l_del_button, next=True)

        #개선일지
        self.log_counter = []
        self.log_text = []
        for i in range(self.num_log):
            self.log_counter.append(QSpinBox())
            self.log_counter[-1].setMaximum(999999)
            self.log_counter[-1].valueChanged.connect(self.lUpdate)
            self.log_text.append(QLineEdit())
            self.addWidget(self.log_counter[-1])
            self.addWidget(self.log_text[-1], 3, next=True)

        #저장, 불러오기, 출력 버튼
        save_button = QPushButton('저장')
        save_button.clicked.connect(self.save)
        load_button = QPushButton('불러오기')
        load_button.clicked.connect(self.loadMount)
        export_button = QPushButton('출력')
        export_button.clicked.connect(self.export)
        self.addWidget(save_button)
        self.addWidget(load_button)
        self.addWidget(export_button, 2, next=True)

    def export(self):
        '''출력한다'''
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
        for habbit in self.h_name:
            idx = self.h_name.index(habbit)
            #아날로그 습관일 때
            if self.h_order[idx] < 'b':
                out_str += '%s : %0.1f / %0.1f\n' %(habbit.text(), self.h_check[idx].value(), self.h_count[idx].value())
            #디지털 습관일 때
            else:
                out_str += '%s : %d / %d\n' %(habbit.text(), self.h_check[idx].isChecked(), self.h_count[idx].value())
        if self.settings.value('linebreak'):
            out_str += '\n'
        out_str += self.settings.value('note') + '\n'
        for log in self.log_text:
            idx = self.log_text.index(log)
            out_str += '%d. %s\n' %(self.log_counter[idx].value(), log.text())

        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(out_str, mode=cb.Clipboard)
        msg = QMessageBox()
        msg.setWindowTitle('오늘의 개선일지')
        msg.setText(out_str)
        msg.buttonClicked.connect(self.expSave)
        msg.exec_()

    def addHabbit(self):
        '''습관을 추가한다'''
        message = QMessageBox()
        message.setWindowTitle('습관 추가')
        message.addButton(QPushButton('디지털'), QMessageBox.YesRole)
        message.addButton(QPushButton('아날로그'), QMessageBox.NoRole)
        message.addButton(QPushButton('취소'), QMessageBox.RejectRole)
        ok = message.exec_()
        #취소가 아닐 때
        if ok < 2:
            #아날로그 습관 추가
            if ok > 0:
                self.hLog.habbit.append(['a', '', 0])
            #디지털 습관 추가
            else:
                self.hLog.habbit.append(['d', '', 0])
        self.clear()
        self.setUI()
        self.mount()

    def delHabbit(self):
        '''마지막 습관을 삭제한다'''
        message = QMessageBox()
        message.setWindowTitle('습관 삭제')
        message.setText('습관 : %s 삭제됩니다.')
        message.addButton(QPushButton('예'), QMessageBox.YesRole)
        message.addButton(QPushButton('아니오'), QMessageBox.NoRole)
        ok = message.exec_()
        if ok < 1:
            self.hLog.habbit.pop()
            self.clear()
            self.setUI()
            self.mount()

    def addLog(self):
        '''개선일지를 추가한다'''
        self.num_log += 1
        self.clear()
        self.setUI()
        self.mount()

    def delLog(self):
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

    def hUpdate(self):
        '''카운터 변화를 반영한다'''
        idx = self.h_check.index(self.sender())
        #아날로그 카운터일 때
        if self.h_order[idx] < 'b':
            self.h_count[idx].setValue(self.h_log.habbit[idx][2] + self.h_check[idx].value())
        #디지털 카운터일 때
        else:
            self.h_count[idx].setValue(self.h_count[idx].value() - (-1)**(self.h_check[idx].isChecked()))

    def lUpdate(self):
        '''개선일지 변화를 반영한다'''
        idx = self.log_counter.index(self.sender())
        value = self.sender().value()
        for log_counter in self.log_counter:
            c_idx = self.log_counter.index(log_counter)
            log_counter.setValue(value - idx + c_idx)

    def d_day_update(self):
        '''날짜 조작에 따라 D-day 카운터를 갱신한다'''
        d_day = self.b_date.date().daysTo(self.c_date.date()) + 1
        self.d_day.setText('D+%d' %d_day)

    def addWidget(self, t_widget, width=1, next=False):
        '''위젯을 추가한다'''
        self.grid.addWidget(t_widget, self.row_count, self.col_count, 1, width)
        if next:
            self.row_count += 1
            self.col_count = 0
        else:
            self.col_count += width

    def save(self):
        '''self.hLog의 데이터를 저장한다'''
        self.hLog.date = self.b_date.date()
        self.hLog.habbit = []
        for habbit in self.h_name:
            idx = self.h_name.index(habbit)
            self.hLog.habbit.append([self.h_order[idx], habbit.text(), self.h_count[idx].value()])
        self.hLog.counter = self.log_counter[-1].value()

        with shelve.open(self.db_name) as data:
            data['h_log'] = self.hLog

    def expSave(self):
        '''데이터를 출력하고, 일지 카운터를 +1 한 후 저장한다'''
        self.hLog.date = self.b_date.date()
        self.hLog.habbit = []
        for habbit in self.h_name:
            idx = self.h_name.index(habbit)
            self.hLog.habbit.append([self.h_order[idx], habbit.text(), self.h_count[idx].value()])
        self.hLog.counter = self.log_counter[-1].value() + 1

        with shelve.open(self.db_name) as data:
            data['h_log'] = self.hLog

        if self.settings.value('autoVerify'):
            wdays='월화수목금토일'
            input_date = self.c_date.date().toString('M/d ') + wdays[self.c_date.date().toPyDate().weekday()]
            input_name = self.settings.value('nickname')
            try:
                gapi = INote_gdapi.gAPI(self.settings.value('sheetID'))
                name_row = gapi.findName(input_name)
                date_column = gapi.findDate(input_date)
                gapi.updateVerification(name_row, date_column)
                data = gapi.getVerificationInfo(name_row)
                msg = QMessageBox()
                msg.setWindowTitle('자동인증 완료!')
                update_msg = '자동인증이 완료되었습니다. \n 이번달에 총 %d회, 누적 총 %d회 인증하셨습니다.'%(data[0], sum(data))
                msg.setText(update_msg)
                msg.exec_()
            except:
                msg = QMessageBox()
                msg.setWindowTitle('자동인증 실패!')
                error_msg = '자동인증이 실패했습니다. ID와 닉네임을 확인해주세요. \n 최초 기동이신 경우, 재시도해주세요.'
                msg.setText(error_msg)
                msg.exec_()

    def load(self):
        '''self.hLog에 저장된 데이터를 불러온다'''
        #데이터 파일 존재를 확인
        if os.path.isfile(self.db_name+'.dat'):
            with shelve.open(self.db_name) as data:
                #데이터 내 세이브의 존재를 확인
                if 'h_log' in data:
                    self.hLog = data['h_log']
                #데이터 내 세이브 없을 때
                else:
                    no_db = QMessageBox()
                    no_db.setWindowTitle('환영합니다')
                    no_db.setText('개선일지를 새롭게 시작합니다')
                    no_db.exec_()
        #파일 자체가 없을 때
        else:
            no_file = QMessageBox()
            no_file.setWindowTitle('환영합니다')
            no_file.setText('개선일지를 새롭게 시작합니다')
            no_file.exec_()

    def loadMount(self):
        '''self.load 이후에 self.mount를 수행한다'''
        self.load()
        self.mount()

    def mount(self):
        '''self.hLog의 데이터를 어플리케이션에 표시한다'''
        self.b_date.setDate(self.hLog.date)
        #저녁 6시 전에 작성하는 경우 :
        if datetime.datetime.now().hour < 18:
            date = datetime.datetime.today() - datetime.timedelta(days=1)
            self.c_date.setDate(date)
        else:
            self.c_date.setDate(datetime.date.today())
        for habbit in self.hLog.habbit:
            idx = self.hLog.habbit.index(habbit)
            self.h_order[idx] = habbit[0]
            self.h_name[idx].setText(habbit[1])
            self.h_count[idx].setValue(habbit[2])
        self.log_counter[0].setValue(self.hLog.counter)

    def clear(self):
        '''어플리케이션 상의 위젯들을 제거한다'''
        for row in range(0, self.grid.rowCount()):
            for column in range(0, self.grid.columnCount()):
                item = self.grid.itemAtPosition(row, column)
                if item != None:
                    widget = item.widget()
                    if widget != None:
                        self.grid.removeWidget(widget)
                        widget.deleteLater()

    def setLabel(self, label_name, c_align=True, frame=True):
        '''정해진 스타일의 레이블을 리턴한다'''
        label = QLabel(label_name)
        if c_align:
            label.setAlignment(Qt.AlignCenter)
        if frame:
            label.setFrameShape(QFrame.Panel)
        return label

    def showSettings(self):
        self.setting_widget = habbit_settings.HabbitSettings(self.settings)
        self.setting_widget.show()

class HabbitLog():
    '''개선일지 데이터 구조체'''
    def __init__(self):
        #데이터 구조체 버전
        self.version = 2

        #시작일자
        self.date = datetime.date.today()

        #습관 : a/d - 습관명 - 카운트
        self.habbit = []

        #개선일지 카운터
        self.counter = 1
