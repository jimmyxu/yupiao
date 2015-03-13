#!/usr/bin/python2
# vim: set fileencoding=utf-8:

import datetime
import math
import os
import random
import re
import requests
import json
import tempfile
from train_list import train_list
from station_name import station_name

requests.packages.urllib3.disable_warnings()

today = (datetime.datetime.now() + datetime.timedelta(hours=8)).date()
base = 'https://kyfw.12306.cn/otn/lcxxcx/query'

def w(s):
    return u'0' if s == u'无' else s

class TrainQueryError(Exception):
    pass

class TrainQuery:
    def __init__(self, fz, dz, traincode='', date=today):
        self.s = requests.session()
        self.s.headers.update({
            'Referer': 'https://kyfw.12306.cn/otn/lcxxcx/init',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',})
        telecode = lambda z: (station_name.has_key(z) and
                              (station_name[z], True) or (z.upper(), False))
        self.fz, self.fztc = telecode(fz)
        self.dz, self.dztc = telecode(dz)
        self.traincode = traincode.lstrip('-').upper()
        self.exclude = traincode.startswith('-')
        self.date = date

    def query(self):
        if (self.fz not in station_name.values() or
            self.dz not in station_name.values()):
            raise TrainQueryError(u'指定车站不存在于station_name.js')

        #r = self.s.get('https://kyfw.12306.cn/otn/leftTicket/init')

        trainno = ''
        payload = [('purpose_codes', 'ADULT'),
                   ('queryDate', str(self.date)),
                   ('from_station', self.fz),
                   ('to_station', self.dz),]
        r = self.s.get(base, params=payload, verify=False)
        if r.status_code != 200:
            raise TrainQueryError(u'上游出错(%d)' % r.status_code)
        try:
            if r.text == u'-1':
                raise TypeError
            t = r.json()['data']['datas']
        except TypeError:
            raise TrainQueryError(u'上游未返回数据')
        except KeyError:
            if r.json().has_key('data') and r.json()['data'].has_key('message'):
                raise TrainQueryError(r.json()['data']['message'])
            else:
                raise TrainQueryError(u'上游未返回有效内容')
        if not t:
            return {}

        result = {}
        count = 0
        for data in t:
            count += 1
            try:
                if self.exclude:
                    if data['station_train_code'][0] in self.traincode:
                        continue
                elif self.traincode:
                    if self.traincode.isalpha():
                        if not data['station_train_code'][0] in self.traincode:
                            continue
                    try:
                        if not data['train_no'] in [train_list[str(self.date)][x] for x in self.traincode.split(',')]:
                            continue
                    except KeyError:
                        raise TrainQueryError(u'车次不存在，或日期不在预售期内')
            except IndexError:
                raise

            try:
                tq = u'%s(%s->%s)' % (data['station_train_code'],
                        data['start_station_name'], data['end_station_name'])
            except KeyError:
                tq = text[1]

            text = [count, tq, data['from_station_name'], data['to_station_name'],
                data['start_time'], data['arrive_time'], data['lishi'],
                w(data['swz_num']), w(data['tz_num']), w(data['zy_num']), w(data['ze_num']),
                w(data['gr_num']), w(data['rw_num']), w(data['yw_num']),
                w(data['rz_num']), w(data['yz_num']), w(data['wz_num']), w(data['qt_num']),]

            if ((self.fztc or data['from_station_telecode'] == self.fz) and
                (self.dztc or data['to_station_telecode'] == self.dz)):
                result[count] = text[1:]

        return result

if __name__ == '__main__':
    tq = TrainQuery('SHH', 'XAY', traincode='-D', date=today + datetime.timedelta(8))
    data = tq.query()
    for d in sorted(data.keys()):
        print ('%d\t%s' % (d, str(data[d]))).decode("string_escape")
