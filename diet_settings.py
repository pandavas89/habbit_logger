import os.path
import datetime
import sys
import shelve

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from common_settings import CommonSettings

class DietSettings(CommonSettings):
    '''식단일기 설정 위젯'''
    def __init__(self, parent):
        super(DietSettings, self).__init__(parent)

        self.setWindowTitle('[먹은거] 설정')

        #출력 순서 데이터
        self.checker_list = ['linebreak', 'weekday', 'calory', 'autoVerify']
        self.text_list = ['header', 'goal', 'action', 'meal', 'deed', 'spreadsheet ID', 'nickname']

        self.setUI()
        self.mount()

    def setUI(self):
        '''UI를 설정한다'''
        self.addCategory('출력')
        self.addCheckerOption('항목 사이 칸 띄우기')
        self.addTextOption('헤더')
        self.addCheckerOption('요일 출력')
        self.addTextOption('목표')
        self.addTextOption('활동')
        self.addTextOption('식단')
        self.addCheckerOption('칼로리 추적')
        self.addTextOption('잘한일')

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
        out_str += '%s%s\n' %(self.text[1].text(), '건강한 삶')
        if self.checker[0].isChecked():
            out_str += '\n'
        out_str += self.text[2].text() + '\n'
        action_list = [['운동', 1, 7], ['식단기록', 0, 22]]
        for action in action_list:
            idx = action_list.index(action)
            out_str += '%s%d / %d\n' %(action[0], action[1], action[2])
        if self.checker[0].isChecked():
            out_str += '\n'
        out_str += self.text[3].text()
        calory_list = [2200, 1900]
        if self.checker[2].isChecked():
            out_str += '%dkcal (%s)' %(calory_list[0], calory_list[1] - calory_list[0])
        out_str += '\n'
        meal_list = [['아침', '스무디'], ['점심', '된장찌개정식'], ['저녁', '닭가슴살 샐러드']]
        for meal in meal_list:
            out_str += '- %s : %s\n' %(meal[0], meal[1])
        if self.checker[0].isChecked():
            out_str += '\n'
        out_str += self.text[4].text() + '\n'
        deed_list = [[16, '배가 고팠지만 간식을 잘 참았다.']]
        for deed in deed_list:
            out_str += '%d. %s\n' %(deed[0], deed[1])

        self.preview_text.setText(out_str)

    def save(self):
        super(DietSettings, self).save()
        self.parent.refresh()

if __name__ == "__main__":
    application = QApplication(sys.argv)
    main_widget = DietSettings('')
    main_widget.show()
    sys.exit(application.exec_())
