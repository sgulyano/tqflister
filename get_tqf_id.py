# import requests
# import json
# import re
# from bs4 import BeautifulSoup

from google.oauth2 import service_account

from sheet import TQFSheet
from tqfreader import TQFReader, parse_tqf3, parse_tqf5

import argparse
parser = argparse.ArgumentParser(description='Scrap TQF 3 or 5 from reg.tu.ac.th')
parser.add_argument("tqf", help="TQF Type (either 3 or 5)", type=int)
args = parser.parse_args()

print('==================')
print(f'TQF: {args.tqf}')
print('==================')

# URL1 = 'https://web.reg.tu.ac.th/wwwtqf/coursespec.aspx'
MAX_ITER = 5#1000

# s = requests.Session()
# r = s.get(URL1)

# data = {
#     'pageNumber': 1,
#     'itemPerPage': 0,
#     'in_coursesemesterid': '',
#     'in_classid': '',
#     'in_tqftype': '0%d' % (args.tqf),
#     'in_pagemode': 'P'
# }


# set initial classid value
if args.tqf == 3:
    cid = 168196
    parse_tqf = parse_tqf3
elif args.tqf == 5:
    cid = 661456
    parse_tqf = parse_tqf5
else:
    raise Exception('Unknown TQF')

# connect to google sheet
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
secret_file = 'token_tqf.json'
credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=SCOPES)

sheet_tqf = TQFSheet(args.tqf, credentials)

prev_df = sheet_tqf.read_data()

# resume from previous search, 
if prev_df.empty:
    print(f'No previous TQF{args.tqf} data available!')
else:
    cid = prev_df['classid'].max()+1

# initialize tqfreader
reader = TQFReader(args.tqf)

# search tqf
print(f'Start from classid: {cid}')
course_data = []

for cid in range(cid, cid + MAX_ITER):
    # # retrieve data from reg
    # if args.tqf == 3:
    #     data['in_coursesemesterid'] = str(cid)
    # elif args.tqf == 5:
    #     data['in_classid'] = str(cid)
    # else:
    #     raise Exception('Unknown TQF')

    # URL2 = 'https://web.reg.tu.ac.th/wwwtqf/coursespec.aspx?__uikWsMth=AJAXWS_CourseSpecList'

    # p = s.post(URL2, data=data)

    # couldn't find info, skip
    # if p.status_code == 500:    
    #     s = requests.Session()
    #     r = s.get(URL1)
    #     print(cid, ' Status Code 500 ---> Skipped')
    #     continue

    div_text = reader.get_cid(cid)
    if div_text is None:
        print(cid, ' Status Code 500 ---> Skipped')
        continue

    _, _, _, en_name, _, year, _, sec = parse_tqf(div_text, cid)
    
    # extract info 
    # div_text = json.loads(p.text)
    
    # if div_text['body']:
    #     course_id_soup = BeautifulSoup(div_text['body'][1], 'html.parser')
        
    #     course_id = course_id_soup.findAll('tr')[-2:]
    #     en_name = course_id[1].text.strip().split('\n')[0]

    #     semyear_soup = BeautifulSoup(div_text['body'][5], 'html.parser')
    #     semyear = semyear_soup.findAll('tr')[1].text.strip()
    #     year_regex = re.search('[0-9][0-9][0-9][0-9]', semyear)
    #     if year_regex:
    #         year = year_regex.group(0)
    #     else:
    #         year = ''

    #     sec = ''
    #     if args.tqf == 5:
    #         sec_soup = BeautifulSoup(div_text['body'][4], 'html.parser')
    #         sec_regex = re.search('[0-9][0-9][0-9][0-9][0-9][0-9]', sec_soup.text)
    #         if sec_regex:
    #             sec = sec_regex.group(0)
    if en_name is not None:
        print(f'[{cid}] {en_name}, Year: {year}')

        if en_name.strip().startswith('DSI') or sec.strip().startswith('65050'):
            course_data.append([cid, en_name, year])

sheet_tqf.write_data(course_data)