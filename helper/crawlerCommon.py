import csv

# CLASS 명
BUTTONCLASS = "btn btn-outline-blue btn_matchcenter"
ACLDIVCLASS = "clearfix team-score"

def getButtonList(soup, league_str):
    if league_str in ["K1", "K2", "R"]:
        match_list = soup.findAll('button', class_=BUTTONCLASS)
    elif league_str == "ACL":
        match_list = soup.findAll('div', class_=ACLDIVCLASS)
    else:
        print("None")
    return match_list

def saveAsCsv(year, month, result, league_str, dataframe, filename):
    with open('{}_{}_{}_{}.csv'.format(filename, league_str, year, month), "w") as output:  # 크롤링한 결과물들을 csv파일의 형태로 저장
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(dataframe)
        for index, val in enumerate(result):
            try:
                writer.writerow(val)
            except Exception as e:
                print('index: ', index)
                print(e)

def saveAsCsv2(year, game_idx, result, league_str, dataframe, filename):
    with open('{}_{}_{}_{}.csv'.format(filename, league_str, year, game_idx), "w") as output:  # 크롤링한 결과물들을 csv파일의 형태로 저장
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(dataframe)
        for index, val in enumerate(result):
            try:
                writer.writerow(val)
            except Exception as e:
                print('index: ', index)
                print(e)
