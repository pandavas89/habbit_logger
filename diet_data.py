import datetime

class DietLog():
    '''식단일기 데이터 구조체'''
    def __init__(self):
        #데이터 구조체 버전
        self.version = 4

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
        self.counter = 1
