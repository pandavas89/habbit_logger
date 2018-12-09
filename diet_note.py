import os.path
import datetime
import sys
import shelve

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from common_note import CommonNote
from diet_data import DietLog
from diet_settings import DietSettings

class DietNote(CommonNote):
    '''식단일기 프로그램'''
    def __init__(self, parent=None):
        '''기초적인 내용을 설정한다'''
        super(DietNote, self).__init__(parent)
        self.log = DietLog()
        self.version = 40
        self.log_name = 'd_log'

        #테스트용
        '''
        self.log.date = datetime.date(year=2018, month=12, day=1)
        self.log.goal = '다이어트!!!'
        self.log.action = [['공복운동', 10],['간헐적 단식', 2]]
        self.log.m_list = ['아침', '점심', '저녁', '간식']
        self.log.counter = 34
        '''

        #설정을 적용한다.
        self.settings = QSettings('pandavas', 'DietNote')
        if not(self.settings.value('init')):
            self.settings.setValue('init', 1)
            self.settings.setValue('header', '[먹은거]#DAY_')
            self.settings.setValue('goal', '1. 목표 : ')
            self.settings.setValue('action', '2. 활동')
            self.settings.setValue('meal', '3. 식단')
            self.settings.setValue('calory', 0)
            self.settings.setValue('deed', '4. 잘한일')
            self.settings.setValue('weekday', 1)
            self.settings.setValue('linebreak', 1)
            self.settings.setValue('autoVerify', 0)

        self.num_log = 1

        self.setWindowTitle('[먹은거] v%0.2f' %(self.version/100))

        self.load()
        self.setUI()
        self.mount()

    def setUI(self):
        '''UI를 설정한다'''
        #d-day
        self.addDdayCounter()

        #목표
        self.addCategory('목표')
        self.goal = QLineEdit()
        self.addWidget(self.goal, next=True)

        #활동
        self.addCategory('활동')
        add_action_button = QPushButton('추가')
        add_action_button.clicked.connect(self.addAction)
        del_action_button = QPushButton('제거')
        del_action_button.clicked.connect(self.delAction)
        self.addWidget(add_action_button)
        self.addWidget(del_action_button, next=True)
        self.addCaloryCounter()
        for action in self.log.action:
            self.addDigitalCounter(action[0])

        #식단
        self.addCategory('식단')
        self.meal_name = []
        self.meal_text = []
        self.addMeal(self.log.m_list)

        #잘한거
        self.addCategory('잘한일')
        add_log_button = QPushButton('추가')
        add_log_button.clicked.connect(self.addlogBtn)
        del_log_button = QPushButton('제거')
        del_log_button.clicked.connect(self.delLogBtn)
        self.addWidget(add_log_button)
        self.addWidget(del_log_button, next=True)
        for i in range(self.num_log):
            self.addLog()

    def mount(self):
        '''self.log의 데이터를 어플리케이션에 반영한다'''
        self.b_date.setDate(self.log.date)
        self.goal.setText(self.log.goal)
        if self.settings.value('calory'):
            self.g_calory.setValue(self.log.c_goal)
        for action in self.log.action:
            idx = self.log.action.index(action)
            self.name[idx].setText(action[0])
            self.counter[idx].setValue(action[1])
        self.log_counter[0].setValue(self.log.counter)

    def addCaloryCounter(self):
        '''칼로리 카운터를 추가한다'''
        if self.settings.value('calory'):
            self.c_calory = QSpinBox()
            self.c_calory.setMaximum(9999)
            self.c_calory.valueChanged.connect(self.caloryUpdate)
            self.g_calory = QSpinBox()
            self.g_calory.setMaximum(9999)
            self.g_calory.valueChanged.connect(self.caloryUpdate)
            self.d_calory = QLabel()
            self.d_calory.setAlignment(Qt.AlignCenter)
            self.addWidget(self.c_calory)
            self.addWidget(self.g_calory)
            self.addWidget(self.d_calory, next=True)

    def caloryUpdate(self):
        '''칼로리 데이터를 갱신한다'''
        if self.settings.value('calory'):
            d_calory = self.c_calory.value() - self.g_calory.value()
            self.d_calory.setText('%+1.0f' %d_calory)
            if d_calory > 0:
                self.d_calory.setStyleSheet("QLabel { color: red; font-weight: bold;}")
            else:
                self.d_calory.setStyleSheet("QLabel { color: green; font-weight: bold;}")

    def addAction(self):
        '''활동을 추가한다'''
        self.log.action.append(['', 0])
        self.clear()
        self.setUI()
        self.mount()

    def delAction(self):
        '''활동을 제거한다'''
        if len(self.log.action) > 1:
            self.log.action.pop()
            self.clear()
            self.setUI()
            self.mount()

    def addMeal(self, meal_list):
        '''식단을 추가한다'''
        #최초 기동시
        if len(meal_list) < 1:
            meal_list = ['아침', '점심', '저녁', '간식']

        for meal in meal_list:
            self.meal_name.append(QLineEdit(meal))
            self.meal_name[-1].setFixedWidth(80)
            self.meal_text.append(QLineEdit())
            self.addWidget(self.meal_name[-1])
            self.addWidget(self.meal_text[-1], next=True)

    def addlogBtn(self):
        '''잘한일을 추가한다'''
        self.num_log += 1
        self.clear()
        self.setUI()
        self.mount()

    def delLogBtn(self):
        '''잘한일을 제거한다'''
        if self.num_log > 1:
            self.num_log -= 1
            self.clear()
            self.setUI()
            self.mount()
        else:
            message = QMessageBox()
            message.setWindowTitle('오류')
            message.setText('마지막 잘한일은 삭제할 수 없습니다')
            message.exec_()

    def save(self, export=False):
        '''저장한다'''
        self.log.date = self.b_date.date()
        self.log.goal = self.goal.text()
        action_list = []
        for action in self.name:
            idx = self.name.index(action)
            action_list.append([self.name[idx].text(), self.counter[idx].value()])
        self.log.action = action_list
        if self.settings.value('calory'):
            self.log.c_goal = self.g_calory.value()
        meal_list = []
        for meal in self.meal_name:
            meal_list.append(meal.text())
        self.log.m_list = meal_list
        if export:
            self.log.counter = self.log_counter[-1].value() + 1
        else:
            self.log.counter = self.log_counter[-1].value()

        super(DietNote, self).save()

    def export(self):
        '''기록을 출력한다'''
        date = self.c_date.date().toString('yyMMdd')
        out_str = self.settings.value('header')
        d_day = self.b_date.date().daysTo(self.c_date.date()) + 1
        out_str += '%s %s' %(d_day, date)
        if self.settings.value('weekday'):
            wdays = '월화수목금토일'
            out_str += wdays[self.c_date.date().toPyDate().weekday()]
        out_str += '\n'
        if self.settings.value('linebreak'):
            out_str += '\n'
        out_str += '%s : %s\n' %(self.settings.value('goal'), self.goal.text())
        if self.settings.value('linebreak'):
            out_str += '\n'
        out_str += self.settings.value('action') + '\n'
        for action in self.name:
            idx = self.name.index(action)
            out_str += '%s : %d / %d\n' %(self.name[idx].text(), self.checker[idx].isChecked(), self.counter[idx].value())
        if self.settings.value('linebreak'):
            out_str += '\n'
        out_str += self.settings.value('meal')
        if self.settings.value('calory'):
            out_str += '%dkcal (%s)' %(self.c_calory.value(), self.d_calory.text())
        out_str += '\n'
        for meal in self.meal_name:
            idx = self.meal_name.index(meal)
            out_str += '- %s : %s\n' %(self.meal_name[idx].text(), self.meal_text[idx].text())
        if self.settings.value('linebreak'):
            out_str += '\n'
        out_str += self.settings.value('deed') + '\n'
        for i in range(self.num_log):
            out_str += '%d. %s\n' %(self.log_counter[i].value(), self.log_text[i].text())

        self.exportMessage(out_str, '오늘의 식단일기')

    def showSettings(self):
        '''설정 화면을 출력한다'''
        self.setting_widget = DietSettings(self)
        self.setting_widget.show()

if __name__ == '__main__':
    application = QApplication(sys.argv)
    main_widget = DietNote()
    main_widget.show()
    sys.exit(application.exec_())
