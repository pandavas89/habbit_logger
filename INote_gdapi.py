from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

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
        date_range = '습관양식!A7:7'
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
        self.gssapi.values().update(spreadsheetId=self.spreadsheet_ID, range=verify_range, valueInputOption='RAW', body=body).execute()

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

if __name__ == '__main__':
    auth = authorize(SPREADSHEET_ID)
    row = auth.findName('판두')
    column = auth.findDate('12/7 금')
    #auth.updateVerification(row, column)
    print(column, row)
