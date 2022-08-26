from flask import Flask, render_template, request

from sheet import read_tqf_data
from google.oauth2 import service_account

from flask_caching import Cache

config={'CACHE_TYPE': 'SimpleCache'} 

app = Flask(__name__)

app.config.from_mapping(config)

cache = Cache(app) 


@app.route('/')
@cache.cached(timeout=3600, query_string=True)
def main_tqf():

    # connect to google sheet
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    secret_file = 'token_tqf.json'
    credentials = service_account.Credentials.from_service_account_file(secret_file, scopes=SCOPES)

    data = read_tqf_data(credentials)

    academic_years = sorted(data['Year'].unique())
    select_year = request.args.get('year', default = academic_years[-1], type = int)
    print(select_year)

    course_list = data[data['Year'] == select_year].to_dict(orient='records')
    
    tqf3a_view_pat = 'https://web.reg.tu.ac.th/wwwtqf/coursespec.aspx?pagemode=P&classid=%d&tqftype=03&documenttitle=3'
    tqf3a_print_pat = 'https://web.reg.tu.ac.th/wwwtqf/coursespecprint.aspx?cmd=1&classid=%d&tqftype=03&documenttitle=3'
    tqf5_view_pat = 'https://web.reg.tu.ac.th/wwwtqf/coursespec.aspx?pagemode=P&classid=%d&tqftype=05&documenttitle=5'
    tqf5_print_pat = 'https://web.reg.tu.ac.th/wwwtqf/coursespecprint.aspx?cmd=1&classid=%d&tqftype=05&documenttitle=5'

    tqf3b_view_pat = 'https://web.reg.tu.ac.th/wwwtqf/coursespec.aspx?pagemode=P&coursesemesterid=%d&tqftype=03&documenttitle=3'
    tqf3b_print_pat = 'https://web.reg.tu.ac.th/wwwtqf/coursespec.aspx?coursesemesterid=%d&tqftype=03&documenttitle=3'
    

    for item in course_list:
        if item['Section']:
            item['Section'] = int(item['Section'])
            item['tqf3_view'] = tqf3a_view_pat % (item['ID'])
            item['tqf3_print'] = tqf3a_print_pat % (item['ID'])
            item['tqf5_view'] = tqf5_view_pat % (item['ID'])
            item['tqf5_print'] = tqf5_print_pat % (item['ID'])
        else:
            item['tqf3_view'] = tqf3b_view_pat % (item['ID'])
            item['tqf3_print'] = tqf3b_print_pat % (item['ID'])
    
    print(course_list)

    return render_template('maintqf.html', 
                           course_list = course_list, 
                           academic_years = academic_years,
                           select_year = select_year)

if __name__ == '__main__':
    app.run(debug=False)