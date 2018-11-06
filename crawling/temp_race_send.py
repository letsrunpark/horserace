from urllib.request import Request, urlopen
import urllib
from bs4 import BeautifulSoup
from pprint import pprint
import pandas as pd
import numpy as np
import time
import os
from lxml import etree
from collections import defaultdict
from collections import OrderedDict
import html5lib
import re
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'}
pd.options.display.max_columns = 100
pd.options.display.max_rows = 100

def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text
replace_dict = {'\xa0':'', '\u200b':'', '\ufeff':'', '\t' : '', '\n' : '', '\r' : '', '\u3000' : ''}

def appending_dict(dictionary, keys):
    for key in keys:
        to_append = eval(key)
        if to_append:
            dictionary[key].append(to_append)
        else:
            dictionary[key].append(None)
    return dictionary

def filling_horses(dictionary1, dictionary2, keys):
    for key in keys:
        dictionary1[key].append(dictionary2[key])
    for i in range(1, 17)[len(keys):]:
        dictionary1["h" + str(i)].append(None)
    return dictionary1

def get_lap_ranks(string):
    ranks = []
    for letter in string:
        ascii_code = ord(letter)
        if 48 <= ascii_code and ascii_code <= 57:
            ranks.append(int(letter))
    return ranks

def get_race_dates_2(loc, page_limits):
    dates = []
    for i in range(page_limits):
        page_num = i + 1
        url = 'http://www.gumvit.com/statv40/result.html?page={0}&loc={1}'.format(page_num, loc)
        print(url)
        req = urllib.request.Request(url, headers = headers)
        page = urllib.request.urlopen(req)
        bs = BeautifulSoup(page.read(), "lxml")
        rlists = bs.findAll('a', {'class' : 'rlist'})
        for rlist in rlists:
            rlist = rlist['href'][19:-2].split(', ')
            rlist[0] = rlist[0][:-1]
            rlist[1] = int(rlist[1])
            dates.append(tuple(rlist))
    dates = sorted(list(set(dates)))
    return dates

def parse_table_from_thtds(thtds):
    key_temp = None
    dic = OrderedDict()
    for thtd in thtds:
        if thtd.name == 'th':
            key_temp = replace_all(thtd.text, replace_dict).strip()
            dic[key_temp] = []
        elif thtd.name == 'td':
            dic[key_temp].append(replace_all(thtd.text, replace_dict).strip())
    return dic

def strip_default(string):
    return string.strip()

re_num = re.compile("[0-9]")
re_nums = re.compile("[0-9]+")
re_prob = re.compile("[0-9]*\.[0-9]+|[0-9]+")


dates = {}
dates['seoul'] = get_race_dates_2('S', 86)


locs = ['S', 'B', 'J']
race_keys = ['url', 'date', 'round', 'weather', 'humidity', 'level', 'distance', 'dan', 'yeon1', 'yeon2', 'yeon3', 'bok', 'ssang', 'bokyeon1', 'bokyeon2', 'bokyeon3', 'sambok', 'samssang', 'horses', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10', 'h11', 'h12', 'h13', 'h14', 'h15', 'h16']
race_result_keys = ['url', 'date', 'round', 'name', 'code', 'rank', 'lane', 'sex', 'age', 'jockey_w', 'rating', 'jockey', 'difference', 'weight', 'dandivi', 'yeondivi', 'equipment', 's1fr', 'c1r', 'c2r', 'c3r', 'c4r', 'g1fr', 's1f', 'c1', 'c2', 'c3', 'c4', 'g3f', 'g1f', 'record']
race_dict = { key : list() for key in race_keys }
for key in race_keys:
    exec(key + "=None")
seoul = dates['seoul']
race_result = pd.DataFrame(columns = race_result_keys)
for i in range(11772, 5424, -200):
    try:
        date = seoul[i]
        print(date)
        url = 'http://www.gumvit.com/statv40/result_detail.html?loc={locs[0]}&racedate={date[0]}&race={date[1]}'.format(locs=locs, date=date)
        req = urllib.request.Request(url, headers = headers)
        page = urllib.request.urlopen(req)
        bs = BeautifulSoup(page.read(), "lxml")
        tables = bs.findAll('td', {'colspan' : '3', 'valign' : 'top'})
        # 날씨, 습도
        table = tables[1].find('table')
        trs = table.findAll('tr')
        temp = trs[0].td.text.strip()
        temp2 = replace_all(temp, replace_dict)
        temp3 = temp2.split()
        weather = temp3[3][:2]
        humidity = temp3[-1][1:-1]
        # 등급
        temp = trs[1].td.text.strip().split()
        level = temp[0]
        distance = temp[1]
        # 배당률
        table = tables[4].find('table')
        trs = table.findAll('tr')
        baedang = trs[5].findAll('td')
        dan = baedang[1].text.strip().split(' ')[-1]
        yeon = baedang[2].text.strip().split(' ')
        yeon1 = yeon[3]
        yeon2 = yeon[5]
        yeon3 = yeon[-1]
        baedang = trs[6].findAll('td')
        bok = baedang[0].text.strip().split(' ')[-1]
        ssang = baedang[1].text.strip().split(' ')[-1]
        baedang = trs[7].findAll('td')
        bokyeon = baedang[0].text.strip().split(' ')
        bokyeon1 = bokyeon[3]
        bokyeon2 = bokyeon[5]
        bokyeon3 = bokyeon[-1]
        sambok = baedang[1].text.strip().split(' ')[-1]
        samssang = trs[8].td.text.strip().split(' ')[-1]
        # 말 숫자
        table = tables[2].find('table')
        thead = bs.new_tag('thead')
        table.tr.wrap(thead)
        df = pd.read_html(str(table))[0]
        df = df.iloc[1:,:]
        horses = df.shape[0]
        # 실제 말
        names = table.findAll('a', {'class' : 'name'})
        horse_keys = race_keys[19:19+horses]
        horse_codes = { key : list() for key in horse_keys }    
        horse_codes['all'] = []
        jockey_codes = []
        horse_num = horses
        for idx, name in enumerate(names):
            if idx % 4 == 0:
                code = name['href'].split("'")[1]        
                current_horse = 'h' + str(horses - horse_num + 1)
                horse_codes[current_horse] = code
                horse_codes['all'].append(code)
                horse_num -= 1
            elif idx % 4 == 1:
                code = name['href'].split("'")[1]
                jockey_codes.append(code)

        dates_co = [date[0] for i in range(horses)]
        round_co = [date[1] for i in range(horses)]
        url_co = [url for i in range(horses)]
        df['date'], df['round'], df['url'] = dates_co, round_co, url_co
        df = df.rename(columns = {
            '순위':'rank', '마번':'lane', '성별':'sex', '연령':'age', '중량':'jockey_w', 
            "레이팅":'rating', '도착차':'difference', '마체중':'weight', '단승식':'dandivi', 
            '연승식':'yeondivi', '마명':'name'
        })
        df['code'] = horse_codes['all']
        df['jockey'] = jockey_codes 
        table = tables[3].find('table')

    except:
        print("error:", url)
    else:
        race_result = race_result.append(df, ignore_index=True)
        filling_horses(race_dict, horse_codes, list(horse_codes.keys())[:-1])
        race_dict['url'].append(url)
        race_dict['date'].append(date[0])
        race_dict['round'].append(date[1])
        race_dict = appending_dict(race_dict, race_keys[3:19])

race_result_df = race_result[race_result_keys]
race_df = pd.DataFrame(race_dict, columns = race_keys)