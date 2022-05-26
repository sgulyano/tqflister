from flask import Flask, render_template, request
import os
import glob
import json
app = Flask(__name__)

@app.route('/')
def main_tqf():
    fl = glob.glob('./data/*.json')

    academic_years = []
    for f in sorted(fl):
        year = int(os.path.splitext(os.path.basename(f))[0])
        academic_years.append(year)

    select_year = request.args.get('year', default = academic_years[-1], type = int)
    print(select_year)

    with open('./data/%d.json' % (select_year), 'r') as f:
        course_list = json.load(f)

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
    
    return render_template('maintqf.html', 
                           course_list = course_list, 
                           academic_years = academic_years,
                           select_year = select_year)

if __name__ == '__main__':
    app.run(debug=False)