# coding=utf-8

from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from tqdm import *
import datetime
import sys
import helper.crawlerCommon as crawlerCommon

# URL 변수
REPORTURL = "http://portal.kleague.com/common/result/result0051popup.do?"
IPTYEAR = "iptMeetYear="
IPTGAMEID = "&iptGameid="
IPTSEQ = "&iptMeetSeq="

# 기타 변수 - 년도나 K1, K2 경기 수 정보는 매년 수정 필요
MONTH = 12
YEAR = 2018
# 경기ID는 로더가 지정할 수 있도록
K1_number = 228
K2_number = 182
CONSOLEGUIDE = "Input league number(league_num 1:K1, 2:K2):  "
DATAFRAME = ['Match_Number', 'League', 'Date', 'Time', 'First_Half_Start_Time', 'First_Half_End_Time', 'Half_Time', 'Second_Half_Start_Time', 'Second_Half_End_Time', 'Stadium', 'Home_Team', 'Home_Score', 'Away_Score', 'Away_Team']
FILENAME = "MatchReport"

def getData(year, game_idx, league_num, league_str, data):
    if league_num == "1":
        game_number = K1_number
    elif league_num == "2":
        game_number = K2_number
    #for i in tqdm(range(game_number)):  # 한번에 크롤링할 페이지 수를 설정해줄 수 있음
    i = game_idx
    try:
        row_data = []
        if league_num == "1":
            report_html = urlopen(REPORTURL + IPTYEAR + year + IPTGAMEID + str(i+1) + IPTSEQ + league_num).read()  # 데이터 보고서 페이지 url
        elif league_num == "2":
            report_html = urlopen(REPORTURL + IPTYEAR + year + IPTGAMEID + str(i+1) + IPTSEQ + league_num).read()  # 데이터 보고서 페이지 url
        else:
            pass
        report = bs(report_html, 'lxml').body   # beautifulsoup 라이브러리를 통해 html을 전부 읽어오는 작업 수행
        month = int(report.findAll('td', class_='bar_bottm_right')[0].get_text().split(' ')[1].split('/')[0])
        date = int(report.findAll('td', class_='bar_bottm_right')[0].get_text().split(' ')[1].split('/')[1].split('(')[0])
        hour = int(report.findAll('td', class_='bar_bottm_right')[0].get_text().split(' ')[2].split(':')[0])  # 시
        minute = int(report.findAll('td', class_='bar_bottm_right')[0].get_text().split(' ')[2].split(':')[1])  # 분

        day = datetime.date(int(year), month, date)
        time = datetime.time(hour, minute)  # 경기 시간
        first_form = report.findAll('td', class_='bar_bottm_right')[1].get_text().split(' ~ ')
        second_form = report.findAll('td', class_='bar_bottm_right')[7].get_text().split(' ~ ')
        first_start_hour = int(first_form[0].split(':')[0])  # 시
        first_start_minute = int(first_form[0].split(':')[1])  # 분
        first_end_hour = int(first_form[1].split(' ')[0].split(':')[0])  # 시
        first_end_minute = int(first_form[1].split(' ')[0].split(':')[1])  # 분
        second_start_hour = int(second_form[0].split(':')[0])  # 시
        second_start_minute = int(second_form[0].split(':')[1])  # 분
        second_end_hour = int(second_form[1].split(' ')[0].split(':')[0])  # 시
        second_end_minute = int(second_form[1].split(' ')[0].split(':')[1])  # 분
        half_time = report.findAll('td', class_='bar_bottm_right')[9].get_text()    # 휴식 시간
        first_half_start_time = datetime.time(first_start_hour, first_start_minute)
        first_half_end_time = datetime.time(first_end_hour, first_end_minute)
        second_half_start_time = datetime.time(second_start_hour, second_start_minute)
        second_half_end_time = datetime.time(second_end_hour, second_end_minute)

        row_data.append(i+1)                                                                                            # 1. Match_ID
        row_data.append(league_str)                                                                                     # 2. League
        row_data.append(day)                                                                                            # 3. Date YYYY-MM-DD
        row_data.append(time.isoformat())                                                                               # 4. Time HH-mm-SS
        row_data.append(first_half_start_time)                                                                          # 5. First_Hlaf_Start_Time
        row_data.append(first_half_end_time)                                                                            # 6. First_Half_End_Time
        row_data.append(half_time)                                                                                      # 7. Half_Time
        row_data.append(second_half_start_time)                                                                         # 8. Second_Half_Start_Time
        row_data.append(second_half_end_time)                                                                           # 9. Second_Half_End_Time
        stadium = report.findAll('tr')[2].findAll('td', class_='bar_bottm_right')[0].get_text().split(' / ')[0]
        row_data.append(stadium)  # 10. Stadium
        hometeam = report.find('table', class_='height110 border01 mb20').findAll('tr')[0].findAll('td')[8].p.get_text()
        row_data.append(hometeam)  # 11. Home_Team
        row_data.append(report.find('table', class_='height110 border01 mb20').findAll('tr')[0].findAll('td')[10].get_text())   # 12. Home_Score
        row_data.append(report.find('table', class_='height110 border01 mb20').findAll('tr')[0].findAll('td')[16].get_text())   # 13. Away_Score
        awayteam = report.find('table', class_='height110 border01 mb20').findAll('tr')[0].findAll('td')[17].p.get_text()
        row_data.append(awayteam) # 14. Away_Team
        data.append(row_data)

    except Exception as e:
        print(e)

    return data

def setBasicInfo(year, game_idx, league_num, league_str):
    # league_num 1:K1, 2:K2 98:R, 99:ACL
    result = []
    data = []
    data = getData(year, game_idx, league_num, league_str, data)
    result.extend(data)
    return result

def crawlMatchCenter(year, game_idx, league_num):
    #while True:
        #league_num = input(CONSOLEGUIDE)
    if league_num in ["1", "2"]:
        league_str = "K" + league_num
    else:
        league_str = "R"
    game_idx2 = int(game_idx) - 1
    result = setBasicInfo(year, game_idx2, league_num, league_str)
    crawlerCommon.saveAsCsv2(year, str(game_idx), result, league_str, DATAFRAME, FILENAME)

if __name__ == "__main__":
    crawlMatchCenter(sys.argv[1], sys.argv[2], sys.argv[3])