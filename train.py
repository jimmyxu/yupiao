#!/usr/bin/python2
# vim: set fileencoding=utf-8:

import cgi
import json
import os
import datetime
import requests
import trainquery.station_name as station_name
import trainquery.train_list as train_list

form = cgi.FieldStorage()

train = form.getvalue('train', '').strip()
date = form.getvalue('date', str(datetime.date.today()))

print 'Content-Type: application/javascript; charset=utf-8'
print 'Cache-Control: private'

if not train:
    print 'Status: 400 Bad Request'
    print
    exit()

if os.getenv('REQUEST_METHOD') == 'HEAD':
    print 'Connection: close'
    print
    exit()

base = 'https://kyfw.12306.cn/otn/czxx/queryByTrainNo'
s = requests.session()
s.headers.update({
    'Referer': 'https://kyfw.12306.cn/otn/czxx/init',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',})

try:
    train_no = train_list[date][train]
except KeyError:
    #print 'Status: 400 Bad Request'
    print
    print json.dumps({'stop': {}, 'stops': ['车次不存在，或日期不在预售期内']}).encode('utf-8')
    exit()

payload = [('train_no', train_list[date][train]),
           ('from_station_telecode', 'XXX'),
           ('to_station_telecode', 'XXX'),
           ('depart_date', date),]
r = s.get(base, params=payload)
t = r.json()['data']['data']

stop = {}
stops = []
station_no = 1
for data in t:
    stops += [data['station_name']]
    stop[data['station_name']] = {'seq': station_no}
    station_no += 1

train = {'stops': stops, 'stop': stop}

print
print json.dumps(train).encode('utf-8')

