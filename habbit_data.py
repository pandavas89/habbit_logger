import datetime

class HabbitLog():
    '''개선일지 데이터 구조체'''
    def __init__(self):
        #데이터 구조체 버전
        self.version = 4

        #시작일자
        self.date = datetime.date.today()

        #습관 : a/d - 습관명 - 카운트
        self.habbit = []

        #개선일지 카운터
        self.counter = 1
