import re
import os
import json
import pandas as pd

import argparse
parser = argparse.ArgumentParser(description='Merge course lists from TQF3 and TQF5 for displaying on website.')
parser.add_argument("tqf3", help="TQF 3 course list file", type=str)
parser.add_argument("tqf5", help="TQF 5 course list file", type=str)
args = parser.parse_args()

print('==================')
print(f'TQF3: {args.tqf3}')
print(f'TQF5: {args.tqf5}')
print('==================')

tqf3 = pd.read_csv(args.tqf3, encoding='utf-8')
tqf5 = pd.read_csv(args.tqf5, encoding='utf-8')

def get_sem(s):
    res = re.findall('ภาคการศึกษาที่\s*(\d)', s)
    if res:
        return res[0]
    return ''

tqf3_clean = pd.concat([tqf3['classid'], 
                        tqf3['TH_name'].str.split("\n", n = 1, expand = True),
                        tqf3['EN_name'].str.split("\n", n = 1, expand = True),
                        tqf3['Semester'].apply(get_sem),
                        tqf3['Year']], axis=1)
tqf3_clean.columns = ['ID', 'TH_code', 'TH_name', 'EN_code', 'EN_name', 'Sem', 'Year']

tqf5_clean = pd.concat([tqf5['classid'], 
                        tqf5['TH_name'].str.split("\n", n = 1, expand = True),
                        tqf5['EN_name'].str.split("\n", n = 1, expand = True),
                        tqf5['Section'],
                        tqf5['Semester'].apply(get_sem),
                        tqf5['Year']], axis=1)
tqf5_clean.columns = ['ID', 'TH_code', 'TH_name', 'EN_code', 'EN_name', 'Section', 'Sem', 'Year']

df = pd.concat([tqf5_clean, tqf3_clean[~tqf3_clean['EN_code'].isin(tqf5_clean['EN_code'])]], axis=0)

for y in df['Year'].unique():
    df_cur = df[df['Year'] == y]
    
    fp = '%d.json' % (y)
    if os.path.exists(fp):
        # combine with previous file
        with open(fp, 'r') as f:
            prev_data = json.load(f)
        df_prev = pd.DataFrame(prev_data)
        
        df_new = pd.concat([df_prev, df_cur[~df_cur['ID'].isin(df_prev['ID'])]], axis=0)
        df_new = df_new.sort_values(['EN_code', 'Section', 'ID'])

    else:
        df_new = df_cur.sort_values(['EN_code', 'Section', 'ID'])
        
    with open('%d.json' % (y), 'w', encoding='utf-8') as f:
        f.write(df_new.to_json(orient="records"))
    print('Done')