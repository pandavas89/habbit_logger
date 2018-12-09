from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

SS_ID = '1A028C_YVvg_km7vLDxAsSVCtL1r_tsduB-LMrUULdfU'
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

class gAPI():
    '''구글 드라이브 제어를 담당한다.'''
    def __init__(self, spreadsheet_ID):
        '''최초 인증을 한다'''
        self.spreadsheet_ID = spreadsheet_ID
        store = file.Storage('token.json')
        creds = store.get()
        #토큰이 없을 때 생성한다.
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        self.service = build('sheets', 'v4', http=creds.authorize(Http()))
        self.gssapi = self.service.spreadsheets()

    def findName(self, target_name):
        '''주어진 이름의 row를 찾아 리턴한다'''
        name_range = '습관양식!A9:A'
        result = self.gssapi.values().get(spreadsheetId=self.spreadsheet_ID, range=name_range).execute()
        names = result.get('values', [])
        for name in names:
            current_name = name[0]
            if target_name == current_name:
                return 9+names.index(name)

    def findDate(self, target_date):
        '''주어진 날짜의 column을 찾는다'''
        date_range = '습관양식!A2:2'
        result = self.gssapi.values().get(spreadsheetId=self.spreadsheet_ID, range=date_range).execute()
        dates = result.get('values', [])
        dates = dates[0]
        for date in dates:
            if target_date == date:
                return col2word(dates.index(date))

    def updateVerification(self, row, column):
        '''인증 정보를 업데이트한다'''
        verify_range = '습관양식!%s%d' %(column, row)
        body = {'values': [['ㅇ']]}
        #권한 조회 방법을 찾을 때 까지 주석처리
        '''
        result = self.gssapi.get(spreadsheetId=self.spreadsheet_ID).execute()
        protection = result['sheets'][0]['protectedRanges']
        found_switch = False

        #편집 권한 여부를 확인한다.
        for ranges in protection:
            range = ranges['range']
            if (word2col(column) >= range['startColumnIndex']) and (word2col(column) <= range['endColumnIndex']):
                if (row >= range['startRowIndex']) and (row <= range['endRowIndex']):
                    if ranges['requestingUserCanEdit']:
                        found_switch = True
                        self.gssapi.values().update(spreadsheetId=self.spreadsheet_ID, range=verify_range, valueInputOption='RAW', body=body).execute()
                    else:
                        msg = QMessage()
                        msg.setTitle('오류')
                        msg.setText('권한이 충분하지 않습니다. 다시 확인해주세요')
                        msg.exec_()
        if not(found_switch):
            self.gssapi.values().update(spreadsheetId=self.spreadsheet_ID, range=verify_range, valueInputOption='RAW', body=body).execute()
        '''
        try:
            self.gssapi.values().update(spreadsheetId=self.spreadsheet_ID, range=verify_range, valueInputOption='RAW', body=body).execute()
            return true
        except:
            return False

    def getVerificationInfo(self, name_row):
        data_range = '습관양식!G%d:H%d' %(name_row, name_row)
        result = self.gssapi.values().get(spreadsheetId=self.spreadsheet_ID, range=data_range).execute()
        datas = result.get('values', [])
        return [int(x) for x in datas[0]]

def col2word(row_digit):
    if row_digit < 26:
        return chr(65 + row_digit)
    else:
        return chr(65 + (row_digit//26 - 1)) + chr(65 + row_digit % 26)

def word2col(letter):
    if len(letter) > 1:
        return (ord(letter[0])-1)*26 + ord(letter[1])
    else:
        return ord(letter) - 65

if __name__ == '__main__':
    auth = gAPI(SS_ID)
    auth.updateVerification(4, 'A')
