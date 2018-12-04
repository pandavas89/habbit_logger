import os.path
import datetime
import sys
import shelve

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import diet_settings

class DietNote(QMainWindow):
    '''식단일기 위젯'''
    def __init__(self, db_name, parent=None):
        '''기초적인 내용을 설정한다'''
        super(DietNote, self).__init__(parent)
        self.db_name = db_name
        self.version = 2
        self.d_version = 2

        self.settings = QSettings('pandavas', 'DietNote')
        if not(self.settings.value('init')):
            self.settings.setValue('init', 1)
            self.settings.setValue('header', '[먹은거]#DAY_')
            self.settings.setValue('goal', '1. 목표')
            self.settings.setValue('action', '2. 활동')
            self.settings.setValue('meal', '3. 식단')
            self.settings.setValue('calory', 0)
            self.settings.setValue('deed', '4. 잘한일')
            self.settings.setValue('weekday', 1)
            self.settings.setValue('linebreak', 1)

        self.dLog = DietLog()

        self.setWindowTitle('[먹은거] v_%0.1f' %(self.version/10))

        self.num_virtue = 1

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
        self.addWidget(self.d_day)
        self.addWidget(setting_button, next=True)

        #목표
        label = self.setLabel('목표')
        self.g_text = QLineEdit()
        self.addWidget(label)
        self.addWidget(self.g_text, 3, next=True)

        #활동
        label = self.setLabel('활동')
        add_action_button = QPushButton('추가')
        add_action_button.clicked.connect(self.addAction)
        del_action_button = QPushButton('삭제')
        del_action_button.clicked.connect(self.delAction)
        self.addWidget(label, 2)
        self.addWidget(add_action_button)
        self.addWidget(del_action_button, next=True)

        #활동 항목
        self.a_text = []
        self.a_check = []
        self.a_count = []
        if len(self.dLog.action) > 0:
            for action in self.dLog.action:
                self.a_text.append(QLineEdit())
                self.a_check.append(QCheckBox())
                self.a_count.append(QSpinBox())
                self.a_count[-1].setMaximum(999999)
                self.addWidget(self.a_text[-1], 2)
                self.addWidget(self.a_check[-1])
                self.addWidget(self.a_count[-1], next=True)

        #식단
        label = self.setLabel('식단')
        add_meal_button = QPushButton('추가')
        add_meal_button.clicked.connect(self.addMeal)
        del_meal_button = QPushButton('삭제')
        self.addWidget(label, 2)
        self.addWidget(add_meal_button)
        self.addWidget(del_meal_button, next=True)

        #칼로리 옵션
        if self.settings.value('calory'):
            self.c_meal = QSpinBox()
            self.c_meal.setMaximum(9999)
            self.c_meal.valueChanged.connect(self.mealUpdate)
            self.g_meal = QSpinBox()
            self.g_meal.setMaximum(9999)
            self.g_meal.valueChanged.connect(self.mealUpdate)
            self.d_meal = QLabel()
            self.d_meal.setAlignment(Qt.AlignCenter)
            self.addWidget(self.c_meal)
            self.addWidget(self.g_meal, 2)
            self.addWidget(self.d_meal, next=True)

        #식단 항목
        self.m_list = []
        self.m_text = []
        if len(self.dLog.m_list) < 1:
            self.autoAddMeal(['아침', '점심', '저녁', '간식'])
        else:
            self.autoAddMeal(self.dLog.m_list)

        #잘한것 헤더
        label = self.setLabel('잘한것')
        self.addWidget(label, 4, next=True)

        #잘한것 항목
        self.v_list = []
        self.v_text = []
        for i in range(self.num_virtue):
            self.v_list.append(QSpinBox())
            self.v_text.append(QLineEdit())
            self.addWidget(self.v_list[-1])
            self.addWidget(self.v_text[-1], 3, next=True)

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


    def load(self):
        '''self.dLog에 저장된 데이터를 불러온다'''
        #데이터 파일 존재를 확인
        if os.path.isfile(self.db_name+'.dat'):
            with shelve.open(self.db_name) as data:
                #데이터 내 세이브의 존재를 확인
                if 'd_log' in data:
                    self.dLog = data['d_log']
                #데이터 내 세이브 없을 때
                else:
                    no_db = QMessageBox()
                    no_db.setWindowTitle('환영합니다')
                    no_db.setText('식단일기를 새롭게 시작합니다')
                    no_db.exec_()
        #파일 자체가 없을 때
        else:
            no_file = QMessageBox()
            no_file.setWindowTitle('환영합니다')
            no_file.setText('식단일기를 새롭게 시작합니다')
            no_file.exec_()

    def mealUpdate(self):
        '''칼로리 변화를 추적한다'''
        self.d_meal.setText('%0.f'%(self.c_meal.value() - self.g_meal.value()))

    def addAction(self):
        '''활동 추가'''
        self.dLog.action.append(['', 0])
        self.clear()
        self.setUI()
        self.mount()

    def delAction(self):
        '''활동 삭제'''
        if len(self.dLog.action) > 1:
            self.dLog.action.pop()
            self.clear()
            self.setUI()
            self.mount()

    def addMeal(self):
        self.dLog.m_list.append('')
        self.clear()
        self.setUI()
        self.mount()

    def delMeal(self):
        self.m_list.pop()
        self.clear()
        self.setUI()
        self.mount()

    def autoAddMeal(self, m_list):
        for meal in m_list:
            self.m_list.append(QLineEdit())
            self.m_list[-1].setText(meal)
            self.m_text.append(QLineEdit())
            self.addWidget(self.m_list[-1])
            self.addWidget(self.m_text[-1], 4, next=True)

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

    def setLabel(self, label_name, c_align=True, frame=True):
        '''정해진 스타일의 레이블을 리턴한다'''
        label = QLabel(label_name)
        if c_align:
            label.setAlignment(Qt.AlignCenter)
        if frame:
            label.setFrameShape(QFrame.Panel)
        return label

    def d_day_update(self):
        '''날짜 조작에 따라 D-day 카운터를 갱신한다'''
        d_day = self.b_date.date().daysTo(self.c_date.date()) + 1
        self.d_day.setText('D+%d' %d_day)

    def save(self):
        '''self.dLog의 데이터를 저장한다'''
        self.dLog.date = self.b_date.date()
        self.dLog.goal = self.g_text.text()
        self.dLog.action = []
        for action in self.a_text:
            idx = self.a_text.index(action)
            self.dLog.action.append([action.text(), self.a_count[idx].value()])
        if self.settings.value('calory'):
            self.dLog.c_goal = self.g_meal.value()
        self.dLog.m_list = []
        for meal in self.m_list:
            self.dLog.m_list.append(meal.text())
        self.dLog.v_count = self.v_list[-1].value()

        with shelve.open(self.db_name) as data:
            data['d_log'] = self.dLog

    def mount(self):
        '''데이터를 어플리케이션에 반영한다'''
        self.b_date.setDate(self.dLog.date)
        self.g_text.setText(self.dLog.goal)
        for action in self.dLog.action:
            idx = self.dLog.action.index(action)
            self.a_text[idx].setText(action[0])
            self.a_count[idx].setValue(action[1])
        self.v_list[0].setValue(self.dLog.v_count)

    def loadMount(self):
        self.load()
        self.mount()

    def export(self):
        '''출력한다'''
        date = self.c_date.date().toString('yyMMdd')
        out_str = self.settings.value('header')
        out_str += '%s %s' %(self.d_day.text(), date)
        if self.settings.value('weekday'):
            wdays = '월화수목금토일'
            out_str += wdays[self.c_date.date().toPyDate().weekday()]
        out_str += '\n'
        if self.settings.value('linebreak'):
            out_str += '\n'
        out_str += '%s : %s\n' %(self.settings.value('goal'), self.g_text.text())
        if self.settings.value('linebreak'):
            out_str += '\n'
        out_str += self.settings.value('action') + '\n'
        for action in self.a_text:
            idx = self.a_text.index(action)
            out_str += '%s : %d / %d\n' %(self.a_text[idx].text(), self.a_check[idx].isChecked(), self.a_count[idx].value())
        if self.settings.value('linebreak'):
            out_str += '\n'
        out_str += self.settings.value('meal')
        if self.settings.value('calory'):
            out_str += '%dkcal (%s)' %(self.c_meal.value(), self.d_meal.text())
        out_str += '\n'
        for meal in self.m_list:
            idx = self.m_list.index(meal)
            out_str += '- %s : %s\n' %(self.m_list[idx].text(), self.m_text[idx].text())
        if self.settings.value('linebreak'):
            out_str += '\n'
        out_str += self.settings.value('deed') + '\n'
        for i in range(self.num_virtue):
            out_str += '%d. %s\n' %(self.v_list[i].value(), self.v_text[i].text())

        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(out_str, mode=cb.Clipboard)
        msg = QMessageBox()
        msg.setWindowTitle('오늘의 식단일기')
        msg.setText(out_str)
        msg.buttonClicked.connect(self.expSave)
        msg.exec_()

    def showSettings(self):
        self.setting_widget = diet_settings.DietSettings(self.settings)
        self.setting_widget.show()

    def expSave(self):
        '''self.dLog의 데이터를 저장한다'''
        self.dLog.date = self.b_date.date()
        self.dLog.goal = self.g_text.text()
        self.dLog.action = []
        for action in self.a_text:
            idx = self.a_text.index(action)
            self.dLog.action.append([action.text(), self.a_count[idx].value()])
        if self.settings.value('calory'):
            self.dLog.c_goal = self.c_goal.value()
        self.dLog.m_list = []
        for meal in self.m_list:
            self.dLog.m_list.append(meal.text())
        self.dLog.v_count = self.v_list[-1].value() + 1

        with shelve.open(self.db_name) as data:
            data['d_log'] = self.dLog

class DietLog():
    '''식단일기 데이터 구조체'''
    def __init__(self):
        #데이터 구조체 버전
        self.version = 2

        #시작일자
        self.date = datetime.date.today()

        #목표
        self.goal = ''

        #체크박스 누적 리스트
        self.action = []

        #식단 칼로리
        self.c_goal = 0

        #식단 리스트
        self.m_list = []

        #잘한일 카운터
        self.v_count = 1
