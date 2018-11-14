from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from tqdm import *
import datetime
import helper.crawlerCommon as crawlerCommon

# URL 변수
URL = "http://www.kleague.com/schedule/get_lists?datatype=html&month="
MATCHCENTERURL = "http://www.kleague.com/match?vw=record&gs_idx="
SELECTLEAGUE = "&select_league="
SELECTLEAGUEYEAR = "&select_league_year=2018"
REPORTURL = "http://portal.kleague.com/common/result/result0051popup.do?"
IPTYEAR = "iptMeetYear=2018"
IPTGAMEID = "&iptGameid="
IPTSEQ = "&iptMeetSeq="

# 기타 변수
MONTH = 12
CONSOLEGUIDE = "Input league number(league_num 1:K1, 2:K2):  "
DATAFRAME = ['Match_ID', 'League', 'Round', 'Date', 'Time', 'First_Half_Start_Time', 'First_Half_End_Time', 'Half_Time', 'Second_Half_Start_Time', 'Second_Half_End_Time', 'Stadium', 'Home_Team', 'Home_Score', 'Away_Score', 'Away_Team']
FILENAME = "MatchReport"

def getData(soup, league_num, league_str, match_list, number_match, data):
    gs_idxList = []
    for i in range(number_match):
        idxList = []
        idxList.append(match_list[i].get('gs_idx'))
        gs_idxList.append(idxList)

    # 공통
    for j in tqdm(range(number_match)):  # 한번에 크롤링할 페이지 수를 설정해줄 수 있음
        try:
            row_data = []
            match_id = gs_idxList[j][0]
            html = urlopen(MATCHCENTERURL + match_id).read()   # 각 매치센터 페이지 사이 url 입력
            body = bs(html, 'lxml').body    # beautifulsoup 라이브러리를 통해 html을 전부 읽어오는 작업 수행
            if league_num == "1":
                report_html = urlopen(REPORTURL + IPTYEAR + IPTGAMEID + match_id + IPTSEQ + league_num).read()  # 데이터 보고서 페이지 url
            elif league_num == "2":
                report_html = urlopen(REPORTURL + IPTYEAR + IPTGAMEID + str(int(match_id)-198) + IPTSEQ + league_num).read()  # 데이터 보고서 페이지 url
            else:
                pass
            report = bs(report_html, 'lxml').body   # beautifulsoup 라이브러리를 통해 html을 전부 읽어오는 작업 수행
            date = body.findAll('div', class_="match-info")[0].get_text().split(" / ")[0].split(" (")[0]  # 경기날짜 YYYY-MM-DD
            hour = int(body.findAll('div', class_="match-info")[0].get_text().split(" / ")[0].split(")  ")[1].split(":")[0])  # 시
            minute = int(body.findAll('div', class_="match-info")[0].get_text().split(" / ")[0].split(")  ")[1].split(":")[1])  # 분
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

            row_data.append(match_id)                                                                               # 1. Match_ID
            row_data.append(league_str)                                                                             # 2. League
            row_data.append(soup.findAll('td', class_="col-rd")[j].get_text().split("R")[0])                        # 3. Round
            row_data.append(date)                                                                                   # 4. Date YYYY-MM-DD
            row_data.append(time.isoformat())                                                                       # 5. Time HH-mm-SS
            row_data.append(first_half_start_time)                                                                  # 6. First_Hlaf_Start_Time
            row_data.append(first_half_end_time)                                                                    # 7. First_Half_End_Time
            row_data.append(half_time)                                                                              # 8. Half_Time
            row_data.append(second_half_start_time)                                                                 # 9. Second_Half_Start_Time
            row_data.append(second_half_end_time)                                                                   # 10. Second_Half_End_Time
            row_data.append(body.findAll('div', class_="match-info")[0].get_text().split(" / ")[2].split("\r")[0])  # 11. Stadium
            row_data.append(body.findAll('div', class_="team-1")[0].get_text())                                     # 12. Home_Team
            row_data.append(body.findAll('div', class_="score")[0].get_text().split("\n")[0].split(" : ")[0])       # 13. Home_Score
            row_data.append(body.findAll('div', class_="score")[0].get_text().split("\n")[0].split(" : ")[1])       # 14. Away_Score
            row_data.append(body.findAll('div', class_="team-2")[0].get_text())                                     # 15. Away_Team
            data.append(row_data)

        except Exception as e:
            print(e)

    return data

def setBasicInfo(league_num, league_str):
    # league_num 1:K1, 2:K2 98:R, 99:ACL
    result = []
    for n in range(MONTH):
        url = urlopen(URL + str(n + 1).zfill(2) + SELECTLEAGUE + league_num + SELECTLEAGUEYEAR).read()  # 크롤링하고자 하는 사이트 url명을 입력
        soup = bs(url, 'lxml').body  # beautifulsoup 라이브러리를 통해 html을 전부 읽어오는 작업 수행

        match_list = crawlerCommon.getButtonList(soup, league_str)
        number_match = len(match_list)

        data = []
        data = getData(soup, league_num, league_str, match_list, number_match, data)
        result.extend(data)
    return result

def crawlMatchCenter():
    while True:
        league_num = input(CONSOLEGUIDE)
        if league_num in ["1", "2"]:
            league_str = "K" + league_num
        else:
            print(CONSOLEGUIDE)
            continue
        result = setBasicInfo(league_num, league_str)
        crawlerCommon.saveAsCsv(result, league_str, DATAFRAME, FILENAME)

if __name__ == "__main__":
    crawlMatchCenter()