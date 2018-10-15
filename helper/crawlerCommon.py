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

def saveAsCsv(result, league_str, dataframe, filename):
    with open(filename + '_{}.csv'.format(league_str), "w") as output:  # 크롤링한 결과물들을 csv파일의 형태로 저장
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(dataframe)
        for index, val in enumerate(result):
            try:
                writer.writerow(val)
            except Exception as e:
                print('index: ', index)
                print(e)
