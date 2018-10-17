from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from tqdm import *
import helper.crawlerCommon as crawlerCommon

# URL 변수
URL = "http://www.kleague.com/schedule/get_lists?datatype=html&month="
MATCHCENTERURL = "http://www.kleague.com/match?vw=record&gs_idx="
SELECTLEAGUE = "&select_league="
SELECTLEAGUEYEAR = "&select_league_year=2018"

# CLASS 명
HOMELINEUP = "homeLineUp"
AWAYLINEUP = "awayLineUp"

# 기타 변수
MONTH = 12
DATAFRAME = ['Match_ID', 'Team', 'Back_Number', 'Name', 'Position', 'Stating/Bench']
LINEUPCONSOLEGUIDE = "Input league number(league_num 1:K1, 2:K2):  "
POSITIONNAME = ["GK", "DF", "MF", "FW", "BENCH"]
STARTINGBENCH = ["선발", "대기"]
FILENAME = "LineUp"

def getLineUp(match_id, line_data, name_team, lineup, position_list):
    for n in range(len(position_list)):
        player_list = position_list[n].findAll('div', class_=lineup)
        for i in range(len(player_list)):
            raw_data = []
            is_name_exist = player_list[i].findAll("span", class_="name")
            if is_name_exist:
                if is_name_exist[0].get_text():
                    raw_data.append(match_id)                                                   # 1. Match_ID
                    raw_data.append(name_team)                                                  # 2. Team
                    raw_data.append(is_name_exist[0].get_text().split(".")[0])                  # 3. Back_Number
                    raw_data.append(is_name_exist[0].get_text().split(".")[1].split(" ")[1])    # 4. Name
                    raw_data.append(POSITIONNAME[n])                                            # 5. Position
                    if POSITIONNAME[n] in POSITIONNAME[0:4]:
                        raw_data.append(STARTINGBENCH[0])                                       # 6. Starting/Bench
                    elif POSITIONNAME[n] in POSITIONNAME[4]:
                        raw_data.append(STARTINGBENCH[1])                                       # 6. Starting/Bench
                    else:
                        pass
                    line_data.append(raw_data)
                else:
                    pass
            else:
                pass

    return line_data

def setBasicInfo(league_num, league_str):
    # league_num 1:K1, 2:K2 98:R, 99:ACL
    result = []
    for n in range(MONTH):
        url = URL + str(n + 1).zfill(2) + SELECTLEAGUE + league_num + SELECTLEAGUEYEAR
        html = urlopen(url).read()  # 크롤링하고자 하는 사이트 url명을 입력
        soup = bs(html, 'lxml').body  # beautifulsoup 라이브러리를 통해 html을 전부 읽어오는 작업 수행

        match_list = crawlerCommon.getButtonList(soup, league_str)
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
                body = bs(html, 'lxml').body    # beautifulsoup 라이브러리를 통해 html을 전부 읽어오는 작업 수행
                match_id = gs_idxList[j][0]     # 각 경기의 고유 번호인 gs_idx를 match_id로 정하여 primary key로 활용

                name_home_team = body.findAll('div', class_="team-1")[0].get_text()
                name_away_team = body.findAll('div', class_="team-2")[0].get_text()
                gk = body.find('ul', class_="list-unstyled gk")
                df = body.find('ul', class_="list-unstyled df")
                mf = body.find('ul', class_="list-unstyled mf")
                fw = body.find('ul', class_="list-unstyled fw")
                bench = body.find('ul', class_="list-unstyled bench")
                position_list = [gk, df, mf, fw, bench]

                home_line_data = []
                away_line_data = []
                home_line_data = getLineUp(match_id, home_line_data, name_home_team, HOMELINEUP, position_list)
                away_line_data = getLineUp(match_id, away_line_data, name_away_team, AWAYLINEUP, position_list)
                line_data = home_line_data + away_line_data
                data_list.extend(line_data)

            except Exception as e:
                print(e)

        result.extend(data_list)

    return result

def crawlLineUp():
    while True:
        league_num = input(LINEUPCONSOLEGUIDE)
        if league_num in ["1", "2"]:
            league_str = "K" + league_num
        else:
            print(LINEUPCONSOLEGUIDE)
            continue
        result = setBasicInfo(league_num, league_str)
        crawlerCommon.saveAsCsv(result, league_str, DATAFRAME, FILENAME)

if __name__ == "__main__":
    crawlLineUp()