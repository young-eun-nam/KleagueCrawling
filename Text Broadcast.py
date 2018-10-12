from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import pandas as pd
from tqdm import *
import csv
import datetime

# URL 변수
URL = "http://www.kleague.com/schedule/get_lists?datatype=html&month="
MATCHCENTERURL = "http://www.kleague.com/match?vw=record&gs_idx="
SELECTLEAGUE = "&select_league="
SELECTLEAGUEYEAR = "&select_league_year=2018"

# CLASS 명
BUTTONCLASS = "btn btn-outline-blue btn_matchcenter"
ACLDIVCLASS = "clearfix team-score"

# 기타 변수
MONTH = 12
EVENTDATAFRAME = ['Match_ID', 'Minute', 'Event', 'Team', 'Back_Number', 'Name']
EVENTCONSOLEGUIDE = "Input league number(league_num 1:K1, 2:K2):  "

def buttonList(soup, league_str):
    if league_str in ["K1", "K2", "R"]:
        match_list = soup.findAll('button', class_=BUTTONCLASS)
    elif league_str == "ACL":
        match_list = soup.findAll('div', class_=ACLDIVCLASS)
    else:
        print("None")
    return match_list

def getData(match_id, name_home_team, name_away_team, min, context):
    game_data_list = []
    for i in range(len(min), -1, -1):
        try:
            row_data = []
            row_data.append(match_id)                                                                           # 1. Match_ID
            row_data.append(min[i].get_text().split("'")[0])                                                    # 2. Minute
            if (name_home_team in context[i].get_text()):
                row_data.append(context[i].get_text().split(name_home_team)[0])                                 # 3. Event
                row_data.append(name_home_team)                                                                 # 4. Team
                row_data.append(context[i].get_text().split(name_home_team)[1].split(", ")[0].split(" ")[2])    # 5. Back_Number
                row_data.append(context[i].get_text().split(name_home_team)[1].split(", ")[1].split(" ")[0])    # 6. Name
            elif (name_away_team in context[i].get_text()):
                row_data.append(context[i].get_text().split(name_away_team)[0])                                 # 3. Event
                row_data.append(name_away_team)                                                                 # 4. Team
                row_data.append(context[i].get_text().split(name_away_team)[1].split(", ")[0].split(" ")[2])    # 5. Back_Number
                row_data.append(context[i].get_text().split(name_away_team)[1].split(", ")[1].split(" ")[0])    # 6. Name
            else:
                row_data.append(context[i].get_text().split(" ")[0])                                            # 3. Event
            game_data_list.append(row_data)
        except:
            pass

    return game_data_list

def setBasicInfo(league_num, league_str):
    # league_num 1:K1, 2:K2 98:R, 99:ACL
    result = []
    for n in range(MONTH):
        url = urlopen(URL + str(n + 1).zfill(2) + SELECTLEAGUE + league_num + SELECTLEAGUEYEAR).read()  # 크롤링하고자 하는 사이트 url명을 입력
        soup = bs(url, 'lxml').body  # beautifulsoup 라이브러리를 통해 html을 전부 읽어오는 작업 수행

        match_list = buttonList(soup, league_str)
        match_number = len(match_list)

        # html source에서 각 경기의 고유 번호인 gs_idx를 모두 읽어와 gs_idxList에 저장
        gs_idxList = []
        for i in range(match_number):
            idxList = []
            idxList.append(match_list[i].get('gs_idx'))
            gs_idxList.append(idxList)

        # 공통
        data_list = []
        for j in tqdm(range(match_number)):  # 한번에 크롤링할 페이지 수를 설정해줄 수 있음
            try:
                html = urlopen(MATCHCENTERURL + str(gs_idxList[j][0])).read()  # 각 매치센터 페이지 사이 url 입력
                body = bs(html, 'lxml').body  # beautifulsoup 라이브러리를 통해 html을 전부 읽어오는 작업 수행
                match_id = gs_idxList[j][0]
                name_home_team = body.findAll('div', class_="team-1")[0].get_text()
                name_away_team = body.findAll('div', class_="team-2")[0].get_text()
                min = body.findAll('div', class_="min")
                context = body.findAll('div', class_="context")

                game_data_list = getData(match_id, name_home_team, name_away_team, min, context)
                data_list.extend(game_data_list)

            except Exception as e:
                print(e)

        result.extend(data_list)

    return result

def saveAsCSV(result, league_str):
    c = 0
    with open('TextBroadcast_'+ league_str +'.csv', "w") as output:  # 크롤링한 결과물들을 csv파일의 형태로 저장
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(EVENTDATAFRAME)
        for val in result:
            try:
                writer.writerow(val)
            except:
                print(c)
            c += 1

def crawlTextBroadcast():
    while(True):
        league_num = input(EVENTCONSOLEGUIDE)
        if league_num in ["1", "2"]:
            league_str = "K" + league_num
        else:
            print(EVENTCONSOLEGUIDE)
            continue
        result = setBasicInfo(league_num, league_str)
        saveAsCSV(result, league_str)

if __name__ == "__main__":
    crawlTextBroadcast()