import datetime

class ReadLog():
    '''독서일기 데이터 구조체'''
    def __init__(self):
        #데이터 구조체 버전
        self.version = 4

        #시작 일자
        self.date= datetime.date.today()

        #현재 도서
        self.c_book = []

        #기록
        self.record = []
