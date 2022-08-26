# import requests
# import json
# import re
# from bs4 import BeautifulSoup
import datetime
import json
# import pandas as pd

from google.oauth2 import service_account

from sheet import TQFSheet, write_tqf_data, service_account_info
from tqfreader import TQFReader, parse_tqf3, parse_tqf5


# check only the 5 previous academic year
year = datetime.date.today().year-4+543
month = datetime.date.today().month
if month <= 9:
    year = year-1
print('Data from academic year:', year)

# connect to google sheet
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

print(service_account_info)
secret_file = 'token_tqf.json'
service_account_info = json.load(open(secret_file))
print(service_account_info)
credentials = service_account.Credentials.from_service_account_info(
    service_account_info)
# credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=SCOPES)
# credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)


sheet_tqf3 = TQFSheet(3, credentials)
tqf3_df = sheet_tqf3.read_data(from_year=year)

sheet_tqf5 = TQFSheet(5, credentials)
tqf5_df = sheet_tqf5.read_data(from_year=year)


tqf3_nodup = tqf3_df.merge(tqf5_df, 
                  left_on=['name', 'year'], 
                  right_on=['name', 'year'], 
                  indicator=True, 
                  how='left',
                  suffixes=('', '_y'))
tqf3_nodup = tqf3_nodup[tqf3_nodup['_merge']=='left_only']
print(tqf3_nodup)
print(tqf5_df)


course_data = [['ID','TH_code','TH_name','EN_code','EN_name','Year','Semester','Section']]

reader = TQFReader(3)
for cid in tqf3_nodup['classid']:
    div_text = reader.get_cid(cid)
    _, th_code, th_name, en_code, en_name, year, sem, sec = parse_tqf3(div_text, cid)
    course_data.append((cid, th_code, th_name, en_code, en_name, year, sem, sec))

reader = TQFReader(5)
for cid in tqf5_df['classid']:
    div_text = reader.get_cid(cid)
    _, th_code, th_name, en_code, en_name, year, sem, sec = parse_tqf5(div_text, cid)
    course_data.append((cid, th_code, th_name, en_code, en_name, year, sem, sec))

write_tqf_data(credentials, course_data)