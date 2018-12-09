import os.path
import datetime
import sys
import shelve
import http.client
import json
import webbrowser

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from habbit_note import HabbitNote
from diet_note import DietNote
from read_note import ReadNote

'''
통합 습관노트 어플리케이션
1. updater4pyi를 이용한 어플리케이션 자동 업데이트
2. 보안 강화
'''

class IntegralNote(QTabWidget):
    '''통합 습관노트 어플리케이션'''
    def __init__(self, parent=None):
        #저장 파일 이름
        super(IntegralNote, self).__init__(parent)
        self.db_name = 'Integral_Log.db'
        self.version = 40
        self.version_text = '.'.join('%03d' %self.version)

        self.setWindowTitle('Integral Note v_%s' %(self.version_text))

        self.setUI()
        self.versionCheck()

    def setUI(self):
        '''UI를 설정한다'''
        self.setStyleSheet("QTabWidget { font-weight: bold; font-size: 12pt; } ")
        self.DietNote = DietNote(self.db_name)
        self.HabbitNote = HabbitNote(self.db_name)
        self.ReadNote = ReadNote(self.db_name)
        self.addTab(self.DietNote, '먹은거')
        self.addTab(self.HabbitNote, '내꺼하나')
        self.addTab(self.ReadNote, '한쪽만')

    def versionCheck(self):
        '''github release API를 통해 버전을 체크한다'''
        conn = http.client.HTTPSConnection("api.github.com")
        conn.putrequest("GET", "/repos/pandavas89/habbit_logger/releases")
        conn.putheader("User-Agent", "MyTest")
        conn.endheaders()

        res = conn.getresponse()
        data = res.read().decode('utf-8')

        json_obj = json.loads(data)
        network_version = json_obj[0]['tag_name']
        if network_version[-5:] == '-beta':
            network_version = network_version[1:-5]
        else:
            network_version = network_version[1:]
        network_version = int(''.join(network_version.split('.')))
        if self.version < network_version:
            message = QMessageBox()
            message.setWindowTitle('새로운 업데이트가 있습니다.')
            message.addButton(QPushButton('다운로드'), QMessageBox.YesRole)
            message.addButton(QPushButton('다음에'), QMessageBox.NoRole)
            ok = message.exec_()

            #다운로드가 선택되었을 때
            if ok < 1:
                webbrowser.open(json_obj[0]['html_url'])
                self.close()

if __name__=='__main__':
    application = QApplication(sys.argv)
    main_widget = IntegralNote()
    main_widget.show()
    sys.exit(application.exec_())
