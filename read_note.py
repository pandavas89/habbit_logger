import os.path
import datetime
import sys
import shelve

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import read_settings
import INote_gdapi

class ReadNote(QMainWindow):
    '''독서일기 위젯'''
    def __init__(self, db_name, parent=None):
        super(ReadNote, self).__init__(parent)
        self.db_name = db_name
        self.version = 3
        self.d_version = 2

        self.settings = QSettings('pandavas', 'ReadNote')
        if not(self.settings.value('init')):
            self.settings.setValue('init', 1)
            self.settings.setValue('header', '[한쪽만]#DAY_')
            self.settings.setValue('comment', '오늘의 감상 : ')
            self.settings.setValue('linebreak', 1)
            self.settings.setValue('weekday', 1)
            self.settings.setValue('autoVerify', 0)

        self.rLog = ReadLog()

        self.setWindowTitle('[한쪽만] v_%0.1f' %(self.version/10))

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.grid = QGridLayout()
        main_widget.setLayout(self.grid)

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
        self.addWidget(self.d_day, 2)
        self.addWidget(setting_button, next=True)

        #현재 도서 헤더
        label = self.setLabel('현재 도서')
        r_add_button = QPushButton('기록 추가')
        r_add_button.clicked.connect(self.addRecord)
        r_del_button = QPushButton('기록 삭제')
        r_del_button.clicked.connect(self.delRecord)
        self.addWidget(label, 3)
        self.addWidget(r_add_button)
        self.addWidget(r_del_button, next=True)

        #현재 도서
        self.c_book = QLineEdit()
        self.b_page = QSpinBox()
        self.b_page.setMaximum(9999)
        label = QLabel('~')
        label.setAlignment(Qt.AlignCenter)
        self.e_page = QSpinBox()
        self.e_page.setMaximum(9999)
        self.addWidget(self.c_book, 2)
        self.addWidget(self.b_page)
        self.addWidget(label)
        self.addWidget(self.e_page, next=True)

        #기록
        self.r_name = []
        self.r_check = []
        self.r_count = []
        if len(self.rLog.record) > 0:
            for record in self.rLog.record:
                self.r_name.append(QLineEdit())
                self.r_check.append(QSpinBox())
                self.r_check[-1].setMaximum(9999)
                self.r_count.append(QSpinBox())
                self.r_count[-1].setMaximum(999999)
                self.addWidget(self.r_name[-1], 3)
                self.addWidget(self.r_check[-1])
                self.addWidget(self.r_count[-1], next=True)

        #감상 헤더
        label = self.setLabel('감상')
        self.addWidget(label, 5, next=True)

        #감상
        self.comment = QTextEdit()
        self.addWidget(self.comment, 5, next=True)

        #저장, 불러오기, 출력 버튼
        save_button = QPushButton('저장')
        save_button.clicked.connect(self.save)
        load_button = QPushButton('불러오기')
        load_button.clicked.connect(self.loadMount)
        export_button = QPushButton('출력')
        export_button.clicked.connect(self.export)
        self.addWidget(save_button, 2)
        self.addWidget(load_button)
        self.addWidget(export_button, 2, next=True)

    def save(self):
        '''self.rLog의 데이터를 저장한다'''
        self.rLog.date = self.b_date.date()
        self.rLog.c_book = self.c_book.text()
        self.rLog.c_page = self.e_page.value()
        self.rLog.record = []
        for record in self.r_name:
            idx = self.r_name.index(record)
            self.rLog.record.append([self.r_name[idx].text(), self.r_count[idx].value()])

        with shelve.open(self.db_name) as data:
            data['r_log'] = self.rLog


    def mount(self):
        '''self.rLog의 데이터를 어플리케이션에 표시한다'''
        self.b_date.setDate(self.rLog.date)
        #저녁 6시 전에 작성하는 경우
        if datetime.datetime.now().hour < 18:
            date = datetime.datetime.today() - datetime.timedelta(days=1)
            self.c_date.setDate(date)
        else:
            self.c_date.setDate(datetime.date.today())
        self.c_book.setText(self.rLog.c_book)
        self.b_page.setValue(self.rLog.c_page)
        self.e_page.setValue(self.rLog.c_page)
        for record in self.rLog.record:
            idx = self.rLog.record.index(record)
            self.r_name[idx].setText(record[0])
            self.r_count[idx].setValue(record[1])

    def addRecord(self):
        '''기록을 추가한다'''
        self.rLog.record.append(['', 0])
        self.clear()
        self.setUI()
        self.mount()

    def delRecord(self):
        '''기록을 제거한다'''
        if len(self.rLog.record) > 0:
            self.rLog.record.pop()
            self.clear()
            self.setUI()
            self.mount()

    def addWidget(self, t_widget, width=1, next=False):
        '''위젯을 추가한다'''
        self.grid.addWidget(t_widget, self.row_count, self.col_count, 1, width)
        if next:
            self.row_count += 1
            self.col_count = 0
        else:
            self.col_count += width

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

    def loadMount(self):
        self.load()
        self.mount()

    def load(self):
        '''self.rLog에 저장된 데이터를 불러온다'''
        #데이터 파일 존재를 확인
        if os.path.isfile(self.db_name+'.dat'):
            with shelve.open(self.db_name) as data:
                #데이터 내 세이브의 존재를 확인
                if 'r_log' in data:
                    self.rLog = data['r_log']
                #데이터 내 세이브 없을 때
                else:
                    no_db = QMessageBox()
                    no_db.setWindowTitle('환영합니다')
                    no_db.setText('독서일기를 새롭게 시작합니다')
                    no_db.exec_()
        #파일 자체가 없을 때
        else:
            no_file = QMessageBox()
            no_file.setWindowTitle('환영합니다')
            no_file.setText('독서일기를 새롭게 시작합니다')
            no_file.exec_()

    def d_day_update(self):
        '''날짜 조작에 따라 D-day 카운터를 갱신한다'''
        d_day = self.b_date.date().daysTo(self.c_date.date()) + 1
        self.d_day.setText('D+%d' %d_day)

    def setLabel(self, label_name, c_align=True, frame=True):
        '''정해진 스타일의 레이블을 리턴한다'''
        label = QLabel(label_name)
        if c_align:
            label.setAlignment(Qt.AlignCenter)
        if frame:
            label.setFrameShape(QFrame.Panel)
        return label

    def export(self):
        '''출력한다'''
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
        out_str += '%s %d~%d\n' %(self.c_book.text(), self.b_page.value(), self.e_page.value())
        if self.settings.value('linebreak'):
            out_str += '\n'
        if len(self.rLog.record) > 0:
            for record in self.r_name:
                idx = self.r_name.index(record)
                out_str += '%s : %d / %d\n' %(record.text(), self.r_check[idx].value(), self.r_count[idx].value())
        out_str += self.settings.value('comment')
        out_str += self.comment.toPlainText()

        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(out_str, mode=cb.Clipboard)
        msg = QMessageBox()
        msg.setWindowTitle('오늘의 개선일지')
        msg.setText(out_str)
        msg.buttonClicked.connect(self.expSave)
        msg.exec_()

    def showSettings(self):
        self.setting_widget = read_settings.ReadSettings(self.settings)
        self.setting_widget.show()

    def expSave(self):
        self.save()
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
                error_msg = '자동인증이 실패했습니다. ID와 닉네임을 확인해주세요.\n 최초 기동이신 경우, 재시도해주세요.'
                msg.setText(error_msg)
                msg.exec_()

class ReadLog():
    '''독서일기 데이터 구조체'''
    def __init__(self):
        #데이터 구조체 버전
        self.version = 2

        #시작 일자
        self.date= datetime.date.today()

        #현재 도서
        self.c_book = ''
        self.c_page = 0

        #기록
        self.record = []
