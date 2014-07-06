#!/usr/bin/python2
# vim: set fileencoding=utf-8:

import cgi
import datetime
import email.header
import json
import os
import traceback
from trainquery import TrainQuery, qssj

def getdj(traincode):
    dj = {u'G': u'高速',
          u'C': u'城际',
          u'D': u'动车',
          u'Z': u'直达',
          u'T': u'特快',
          u'K': u'快速',
          u'Y': u'旅游',
          u'L': u'临客',}
    dj.update([(unicode(i), u'普快') for i in xrange(1, 6)])
    dj.update([(unicode(i), u'普客') for i in xrange(6, 9)])

    return dj.get(traincode[0], u'--')

def getqssj(fz, traincode):
    if traincode[0] in u'CD':
        return u'11:00'
    elif traincode[0] in u'G':
        return u'14:00'
    try:
        return qssj.qssj[fz]
    except KeyError:
        return u'null'

form = cgi.FieldStorage()

fz = form.getvalue('fz').strip()
dz = form.getvalue('dz').strip()
train = form.getvalue('train', '').strip()
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
    if isinstance(ex.message, str):
        message = ex.message.decode('utf-8')
    else:
        message = unicode(ex.message)
    message = email.header.Header(message).encode()
    print 'Status: 500 Internal Server Error'
    print 'Content-Type: text/plain'
    print
    print '/*\n%s */' % traceback.format_exc()
    exit()

data = u''
for i in sorted(result.keys()):
    r = result[i]
    other = u''
    rz = r[13] if r[13] != u'--' else r[8]
    yz = r[14] if r[14] != u'--' else r[9]
    if u'*' in r[11] + r[12] + rz + yz + r[15]:
        other += u'%s起售 ' % getqssj(r[1], r[0])
    if r[6] != u'--':
        other += u'商务:%s ' % r[6]
    if r[7] != u'--':
        other += u'特等:%s ' % r[7]
    if r[10] != u'--':
        other += u'高软:%s ' % r[10]
    if r[16] != u'--':
        other += u'其他:%s' % r[16]
    # 日期,#,车次,发站,到站,出发,到达,历时,软卧,硬卧,软座,硬座,其他,无座,等级
    data += u'%s,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s;' % (
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
            rz, # 软座
            yz, # 硬座
            other if other else u'--', # 其他
            r[15], # 无座
            getdj(r[0]), # 等级
            )
data = data[:-1].encode('utf-8')

response = '%s(%s)' % (jsoncallback, json.dumps({'data': data}))
print 'Content-Length: %d' % len(response)
print
print response
