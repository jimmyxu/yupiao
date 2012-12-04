#!/usr/bin/python2
# vim: set fileencoding=utf-8:

import cgi
import datetime
import email.header
import json
import os
import traceback
from trainquery import TrainQuery

def getdj(traincode):
    char = traincode[0]
    if char == 'G':
        return '高速'
    elif char == 'C':
        return '城际'
    elif char == 'D':
        return '动车'
    elif char == 'Z':
        return '直达'
    elif char == 'T':
        return '特快'
    elif char == 'K':
        return '快速'
    elif char == 'Y':
        return '旅游'
    elif char == 'L':
        return '临客'
    elif char >= '1' and char <= '5':
        return '普快'
    elif char >= '6' and char <= '8':
        return '普客'
    else:
        return '--'


form = cgi.FieldStorage()

fz = form.getvalue('fz')
dz = form.getvalue('dz')
train = form.getvalue('train', '')
date = form.getvalue('date', str(datetime.date.today()))
jsoncallback = form.getvalue('jsoncallback')

year, month, day = [int(s) for s in date.split('-')]
date = datetime.date(year, month, day)

print 'Content-Type: application/javascript; charset=utf-8'
print 'Cache-Control: private'

if not fz or not dz or not jsoncallback:
    print 'Status: 400 Bad Request'
    print
    exit()

if os.getenv('REQUEST_METHOD') == 'HEAD':
    print 'Connection: close'
    print
    exit()

try:
    tq = TrainQuery(fz, dz, traincode=train, date=date)
    result = tq.query()
except Exception, ex:
    print 'Status: 500 %s' % email.header.Header(ex.message.decode('utf-8')).encode()
    print
    print '/*\n%s */' % traceback.format_exc()
    exit()

data = ''
for i in sorted(result.keys()):
    r = result[i]
    other = ''
    if r[6] != '--':
        other += '商务:%s ' % r[6]
    if r[7] != '--':
        other += '特等:%s ' % r[7]
    if r[10] != '--':
        other += '高软:%s ' % r[10]
    if r[16] != '--':
        other += r[16]
    # 日期,#,车次,发站,到站,出发,到达,历时,软卧,硬卧,软座,硬座,其他,无座,等级
    data += '%s,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s;' % (
            date, # 日期
            i, # #
            r[0], # 车次
            r[1], # 发站
            r[2], # 到站
            r[3], # 出发
            r[4], # 到达
            r[5], # 历时
            r[11], # 软卧
            r[12], # 硬卧
            r[13] if r[13] != '--' else r[8], # 软座
            r[14] if r[14] != '--' else r[9], # 硬座
            other if other else '--', # 其他
            r[15], # 无座
            getdj(r[0]), # 等级
            )
data = data[:-1]

response = '%s(%s)' % (jsoncallback, json.dumps({'data': data}))
print 'Content-Length: %d' % len(response)
print
print response
