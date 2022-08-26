import requests
import json
import re
from bs4 import BeautifulSoup

class TQFReader:

    URL1 = 'https://web.reg.tu.ac.th/wwwtqf/coursespec.aspx'
    URL2 = 'https://web.reg.tu.ac.th/wwwtqf/coursespec.aspx?__uikWsMth=AJAXWS_CourseSpecList'

    def __init__(self, tqf):
        if tqf != 3 and tqf != 5:
            raise Exception('Unknown TQF')
        self.get_session()
        self.tqf = tqf
        self.data = {
            'pageNumber': 1,
            'itemPerPage': 0,
            'in_coursesemesterid': '',
            'in_classid': '',
            'in_tqftype': '0%d' % (tqf),
            'in_pagemode': 'P'
        }

    def get_session(self):
        self.s = requests.Session()
        self.r = self.s.get(self.URL1)

    def get_cid(self, cid):
        # retrieve data from reg
        if self.tqf == 3:
            self.data['in_coursesemesterid'] = str(cid)
        elif self.tqf == 5:
            self.data['in_classid'] = str(cid)

        p = self.s.post(self.URL2, data=self.data)

        # couldn't find info, skip
        if p.status_code == 500:    
            self.get_session()
            return None
    
        return json.loads(p.text)


def get_sem(s):
    res = re.findall('ภาคการศึกษาที่\s*(\d)', s)
    if res:
        return res[0]
    return ''

def parse_tqf(div_text, cid, tqf):
    if div_text['body'] is None:
        return None, None, None, None, None, None, None, None
    course_id_soup = BeautifulSoup(div_text['body'][1], 'html.parser')
    
    course_id = course_id_soup.findAll('tr')[-2:]
    th_code, th_name = course_id[0].text.strip().split('\n', maxsplit=1)
    en_code, en_name = course_id[1].text.strip().split('\n', maxsplit=1)

    semyear_soup = BeautifulSoup(div_text['body'][5], 'html.parser')
    semyear = semyear_soup.findAll('tr')[1].text.strip()
    
    year_regex = re.search('[0-9][0-9][0-9][0-9]', semyear)
    if year_regex:
        year = year_regex.group(0)
    else:
        year = ''
    
    sem = get_sem(semyear)

    sec = ''
    if tqf == 5:
        sec_soup = BeautifulSoup(div_text['body'][4], 'html.parser')
        sec_regex = re.search('[0-9][0-9][0-9][0-9][0-9][0-9]', sec_soup.text)
        if sec_regex:
            sec = sec_regex.group(0)
        
    return cid, th_code, th_name, en_code, en_name, int(year), int(sem), sec
    
def parse_tqf3(div_text, cid):
    return parse_tqf(div_text, cid, 3)

def parse_tqf5(div_text, cid):
    return parse_tqf(div_text, cid, 5)