import os.path
import datetime
import sys
import shelve
import webbrowser

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from inote_gdapi import gAPI

class CommonNote(QMainWindow):
    '''공통 일지 프로그램'''
    def __init__(self, db_name, parent=None):
        '''기초적인 내용을 설정한다'''
        super(CommonNote, self).__init__(parent)

        self.db_name = db_name
        self.log_name = None

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.stack = QVBoxLayout()
        main_widget.setLayout(self.stack)
        self.widget_row = QHBoxLayout()

        self.bar = self.menuBar()

        self.save_action = QAction('저장(S)', self)
        self.save_action.setShortcut('Ctrl+S')
        self.bar.addAction(self.save_action)
        self.save_action.triggered.connect(self.save)

        self.load_action = QAction('불러오기(L)', self)
        self.load_action.setShortcut('Ctrl+L')
        self.bar.addAction(self.load_action)
        self.load_action.triggered.connect(self.load)

        self.export_action = QAction('출력(P)', self)
        self.export_action.setShortcut('Ctrl+P')
        self.bar.addAction(self.export_action)
        self.export_action.triggered.connect(self.export)

        self.settings_action = QAction('설정(O)', self)
        self.settings_action.setShortcut('Ctrl+O')
        self.bar.addAction(self.settings_action)
        self.settings_action.triggered.connect(self.showSettings)

        self.help_action = QAction('도움말(H)', self)
        self.help_action.setShortcut('Ctrl+H')
        self.bar.addAction(self.help_action)
        self.help_action.triggered.connect(self.helpOpen)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.name = []
        self.checker = []
        self.counter = []
        self.c_value = []

        self.log_counter = []
        self.log_text = []

        self.b_name = []
        self.b_start = []
        self.b_end = []
        self.b_total = []
        self.b_percent = []

    def addCategory(self, category_name):
        '''그룹박스를 추가한다'''
        self.groupbox = QGroupBox(category_name)
        self.groupbox.setStyleSheet("QGroupBox { font-weight: bold; font-size: 12pt; } ")
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

    def addDdayCounter(self):
        '''d-day 카운터를 추가한다'''
        self.addCategory('D-day')
        self.b_date = QDateEdit()
        self.b_date.dateChanged.connect(self.dDayUpdate)
        self.c_date = QDateEdit()
        self.c_date.dateChanged.connect(self.dDayUpdate)
        self.d_day = QLabel('')
        self.d_day.setAlignment(Qt.AlignCenter)
        self.c_date.setDate(datetime.date.today())
        self.addWidget(self.b_date)
        self.addWidget(self.c_date)
        self.addWidget(self.d_day, next=True)

    def addDigitalCounter(self, name):
        '''체커 카운터를 추가한다'''
        self.name.append(QLineEdit(name))
        self.checker.append(QCheckBox())
        self.checker[-1].stateChanged.connect(self.dCheckerUpdate)
        self.counter.append(QSpinBox())
        self.counter[-1].setMaximum(999999)
        self.addWidget(self.name[-1])
        self.addWidget(self.checker[-1])
        self.addWidget(self.counter[-1], next=True)

    def addAnalogCounter(self, name, point=True):
        '''연속 카운터를 추가한다'''
        self.name.append(QLineEdit(name))
        if point:
            self.checker.append(QDoubleSpinBox())
            self.counter.append(QDoubleSpinBox())
        else:
            self.checker.append(QSpinBox())
            self.counter.append(QSpinBox())
        self.checker[-1].setMaximum(9999)
        self.checker[-1].valueChanged.connect(self.aCheckerUpdate)
        self.counter[-1].setMaximum(999999)
        self.counter[-1].valueChanged.connect(self.cValueUpdate)
        self.addWidget(self.name[-1])
        self.addWidget(self.checker[-1])
        self.addWidget(self.counter[-1], next=True)

    def addPageCounter(self, name):
        '''페이지 카운터를 추가한다'''
        self.b_name.append(QLineEdit(name))
        self.b_start.append(QSpinBox())
        self.b_start[-1].setMaximum(9999)
        self.b_end.append(QSpinBox())
        self.b_end[-1].setMaximum(9999)
        self.b_end[-1].valueChanged.connect(self.pageUpdate)
        self.b_total.append(QSpinBox())
        self.b_total[-1].setMaximum(99999)
        self.b_percent.append(QLabel())
        self.addWidget(self.b_name[-1])
        self.addWidget(self.b_start[-1])
        self.addWidget(QLabel('~'))
        self.addWidget(self.b_end[-1])
        self.addWidget(QLabel('/'))
        self.addWidget(self.b_total[-1])
        self.addWidget(self.b_percent[-1], next=True)

    def addLog(self):
        self.log_counter.append(QSpinBox())
        self.log_counter[-1].valueChanged.connect(self.logUpdate)
        self.log_text.append(QLineEdit())
        self.addWidget(self.log_counter[-1])
        self.addWidget(self.log_text[-1], next=True)

    def dDayUpdate(self):
        '''날짜 조작에 따라 D-day 카운터를 갱신한다'''
        d_day = self.b_date.date().daysTo(self.c_date.date()) + 1
        self.d_day.setText('D+%d' %d_day)

    def dCheckerUpdate(self):
        '''체커 변화에 따른 누적값 업데이트'''
        idx = self.checker.index(self.sender())
        self.counter[idx].setValue(self.counter[idx].value() - (-1)**self.sender().isChecked())

    def aCheckerUpdate(self):
        '''카운터 변화에 따른 누적값 업데이트'''
        idx = self.checker.index(self.sender())
        self.counter[idx].setValue(self.c_value[idx] + self.checker[idx].value())

    def cValueUpdate(self):
        '''연속카운터 값을 업데이트한다'''
        idx = self.counter.index(self.sender())
        self.c_value[idx] = self.counter[idx].value() - self.checker[idx].value()

    def logUpdate(self):
        '''일지 카운터를 업데이트한다'''
        idx = self.log_counter.index(self.sender())
        value = self.sender().value()
        for log_counter in self.log_counter:
            c_idx = self.log_counter.index(log_counter)
            log_counter.setValue(value - idx + c_idx)

    def pageUpdate(self):
        '''페이지 카운터를 업데이트한다'''
        idx = self.b_end.index(self.sender())
        if self.b_total[idx].value() > 0:
            percentage = self.sender().value() / self.b_total[idx].value() * 100
            self.b_percent[idx].setText('%0.1f %%' %percentage)

    def exportMessage(self, out_str, title):
        '''결과물을 새 창에 출력하고 클립보드에 복사한다'''

        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(out_str, mode=cb.Clipboard)
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(out_str)
        msg.buttonClicked.connect(lambda x=True: self.save(x))
        msg.exec_()

        if self.settings.value('autoVerify'):
            gdapi = gAPI(self.settings.value('spreadsheet ID'))
            name_row = gdapi.findName(self.settings.value('nickname'))
            date = self.c_date.date().toPyDate()
            date_str = date.strftime('%m/%d ') + '월화수목금토일'[date.weekday()]
            date_col = gdapi.findDate(date_str)
            msg = QMessageBox()
            if gdapi.updateVerification(name_row, date_col):
                v_data = gdapi.getVerificationInfo(name_row)
                msg.setWindowTitle('자동인증 완료')
                msg.setText('이번 달 %d 번, 누적 %d 번 인증하셨습니다.' %(v_data[0], v_data[1]))
            else:
                msg.setWindowTitle('권한 오류')
                msg.setText('시트를 수정할 권한이 없습니다. 직접 인증해주세요.')
            msg.exec_()

    def clear(self):
        '''화면을 초기화한다'''
        for i in reversed(range(self.stack.count())):
            self.stack.itemAt(i).widget().setParent(None)
        self.name = []
        self.checker = []
        self.counter = []
        self.log_counter = []
        self.log_text = []
        self.b_name = []
        self.b_start = []
        self.b_end = []
        self.b_total = []
        self.b_percent = []

    def refresh(self):
        '''화면을 갱신한다'''
        self.clear()
        self.setUI()
        self.mount()

    def load(self):
        '''저장된 데이터를 불러온다'''
        #데이터 파일 존재를 확인
        if os.path.isfile(self.db_name+'.dat'):
            with shelve.open(self.db_name) as data:
                #데이터 내 세이브의 존재를 확인
                if self.log_name in data:
                    self.log = data[self.log_name]
                    self.status_bar.showMessage('불러오기가 완료되었습니다')
                #데이터 내 세이브가 없을 때
                else:
                    no_db = QMessageBox()
                    no_db.setWindowTitle('환영합니다')
                    no_db.setText('새롭게 시작합니다')
                    no_db.exec_()
        #파일 자체가 없을 때
        else:
            no_db = QMessageBox()
            no_db.setWindowTitle('환영합니다')
            no_db.setText('새롭게 시작합니다')
            no_db.exec_()

    def save(self):
        '''self.log의 데이터를 저장한다'''
        with shelve.open(self.db_name) as data:
            data[self.log_name] = self.log
        self.status_bar.showMessage('저장되었습니다')

    def helpOpen(self):
        '''도움말을 출력한다'''
        webbrowser.open('http://pandavas89.github.io/productivity/integral-note-help')

if __name__ == '__main__':
    application = QApplication(sys.argv)
    main_widget = CommonNote()
    main_widget.addCategory('체커 테스트 카테고리')
    main_widget.addDigitalCounter('테스트')
    main_widget.addDigitalCounter('테스트2')
    main_widget.addCategory('연속 테스트 카테고리')
    main_widget.addAnalogCounter('연속 테스트1')
    main_widget.addAnalogCounter('연속 테스트2')
    main_widget.addCategory('개선일지 카테고리')
    main_widget.addLog()

    main_widget.show()
    sys.exit(application.exec_())
