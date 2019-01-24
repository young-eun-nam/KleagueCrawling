from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from tqdm import *
import datetime
import helper.crawlerCommon as crawlerCommon
import sys

# URL 변수
URL = "http://www.kleague.com/schedule/get_lists?datatype=html&month="
MATCHCENTERURL = "http://www.kleague.com/match?vw=record&gs_idx="
SELECTLEAGUE = "&select_league="
SELECTLEAGUEYEAR = "&select_league_year="

# 기타 변수
MONTH = 12
CONSOLEGUIDE = "Input league number(league_num 1:K1, 2:K2 98:R, 99:ACL):  "
DATAFRAME = ['Match_ID', 'League', 'Round', 'Date', 'Time', 'Stadium', 'Home_Team', 'Home_Score', 'Away_Score', 'Away_Team']
FILENAME = "MatchCenter"

def getData(soup, league_str, match_list, number_match, data):
    if league_str in ["K1", "K2", "R"]:

        gs_idxList = []
        for i in range(number_match):
            idxList = []
            idxList.append(match_list[i].get('gs_idx'))
            gs_idxList.append(idxList)

        # 공통
        # for j in tqdm(range(number_match)):  # 한번에 크롤링할 페이지 수를 설정해줄 수 있음
        for j in range(number_match):  # 한번에 크롤링할 페이지 수를 설정해줄 수 있음
            try:
                row_data = []
                html = urlopen(MATCHCENTERURL + str(gs_idxList[j][0])).read()  # 각 매치센터 페이지 사이 url 입력
                body = bs(html, 'lxml').body  # beautifulsoup 라이브러리를 통해 html을 전부 읽어오는 작업 수행
                match_id = gs_idxList[j][0]
                date = body.findAll('div', class_="match-info")[0].get_text().split(" / ")[0].split(" (")[0]  # 경기날짜 YYYY-MM-DD
                hour = int(body.findAll('div', class_="match-info")[0].get_text().split(" / ")[0].split(")  ")[1].split(":")[0])  # 시
                minute = int(body.findAll('div', class_="match-info")[0].get_text().split(" / ")[0].split(")  ")[1].split(":")[1])  # 분
                time = datetime.time(hour, minute)  # 경기 시간

                row_data.append(match_id)                                                                               # 1. Match_ID
                row_data.append(league_str)                                                                             # 2. League
                if league_str in ["K1", "K2"]:
                    row_data.append(soup.findAll('td', class_="col-rd")[j].get_text().split("R")[0].strip())            # 3. Round
                elif league_str == "R":
                    row_data.append("")                                                                                 # 3. Round
                else:
                    print("None")
                row_data.append(date)                                                                                   # 4. Date YYYY-MM-DD
                row_data.append(time.isoformat())                                                                       # 5. Time HH-mm-SS
                row_data.append(body.findAll('div', class_="match-info")[0].get_text().split(" / ")[2].split("\r")[0])  # 6. Stadium
                row_data.append(body.findAll('div', class_="team-1")[0].get_text())                                     # 7. Home_Team
                row_data.append(body.findAll('div', class_="score")[0].get_text().split("\n")[0].split(" : ")[0])       # 8. Home_Score
                row_data.append(body.findAll('div', class_="score")[0].get_text().split("\n")[0].split(" : ")[1])       # 9. Away_Score
                row_data.append(body.findAll('div', class_="team-2")[0].get_text())                                     # 10. Away_Team
                data.append(row_data)

            except Exception as e:
                print(e)

        return data

    elif league_str == "ACL":

        #for i in tqdm(range(number_match)):  # 한번에 크롤링할 페이지 수를 설정
        for i in range(number_match):  # 한번에 크롤링할 페이지 수를 설정
            try:
                date = []
                for j in range(len(soup.findAll('table', class_="table"))):
                    for k in range(len(soup.findAll('table')[0].tbody.findAll('tr'))):
                        date.append(soup.findAll("table")[j].tbody.findAll('tr')[k].get('id').split("y")[0])

                row_data = []
                row_data.append("")                                                                                     # 1. Match_ID
                row_data.append(league_str)                                                                             # 2. League
                row_data.append("")                                                                                     # 3. Round
                row_data.append(date[i])                                                                                # 4. Date YYYY-MM-DD
                row_data.append("")                                                                                     # 5. Time
                row_data.append("")                                                                                     # 6. Stadium
                row_data.append(soup.findAll("div", class_="team-1")[i].get_text().split("\n")[1])                      # 7. Home_Team
                row_data.append(soup.findAll("div", class_="score")[i].get_text().split("\n")[0].split(":")[0])         # 8. Home_Score
                row_data.append(soup.findAll("div", class_="score")[i].get_text().split("\n")[0].split(":")[1])         # 9. Away_Score
                row_data.append(soup.findAll("div", class_="team-2")[i].get_text().split("\n")[2])                      # 10. Away_Team
                data.append(row_data)
            except Exception as e:
                print(e)

        return data

    else:
        print("None")

def setBasicInfo(year, month, league_num, league_str):
    # league_num 1:K1, 2:K2 98:R, 99:ACL
    result = []
    # for n in range(MONTH):
    n = int(month) - 1
    url = urlopen(URL + str(n + 1).zfill(2) + SELECTLEAGUE + league_num + SELECTLEAGUEYEAR + year).read()  # 크롤링하고자 하는 사이트 url명을 입력
    soup = bs(url, 'lxml').body  # beautifulsoup 라이브러리를 통해 html을 전부 읽어오는 작업 수행

    match_list = crawlerCommon.getButtonList(soup, league_str)
    number_match = len(match_list)

    data = []
    data = getData(soup, league_str, match_list, number_match, data)
    result = result + data
    return result

def crawlMatchCenter(year, month, league_num):
    #while True:
    # league_num = input(CONSOLEGUIDE)
    if league_num in ["1", "2"]:
        league_str = "K" + league_num
    elif league_num == "98":
        league_str = "R"
    elif league_num == "99":
        league_str = "ACL"
    '''else:
        print(CONSOLEGUIDE)
        continue'''

    result = setBasicInfo(year, month, league_num, league_str)
    crawlerCommon.saveAsCsv(year, month, result, league_str, DATAFRAME, FILENAME)

if __name__ == "__main__":
    crawlMatchCenter(sys.argv[1], sys.argv[2], sys.argv[3])