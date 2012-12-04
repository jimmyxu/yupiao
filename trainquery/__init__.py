#!/usr/bin/python2
# vim: set fileencoding=utf-8:

import datetime
import math
import os
import random
import re
import requests
import tempfile
from station_name import station_name

today = (datetime.datetime.now() + datetime.timedelta(hours=8)).date()
base = 'http://dynamic.12306.cn/otsquery/query/queryRemanentTicketAction.do?%s'

class TrainQueryError(Exception):
    pass

class TrainQuery:
    def __init__(self, fz, dz, traincode='', date=today):
        self.s = requests.session()
        self.s.config['base_headers']['User-Agent'] = \
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)'
        self.s.config['base_headers']['Referer'] = base % 'method=init'
        self.s.config['base_headers']['X-Requested-With'] = 'XMLHttpRequest'
        telecode = lambda z: (station_name.has_key(z) and
                              (station_name[z], True) or (z.upper(), False))
        self.fz, self.fztc = telecode(fz)
        self.dz, self.dztc = telecode(dz)
        self.traincode = traincode
        self.date = date

    def query(self):
        if (self.fz not in station_name.values() and
            self.dz not in station_name.values()):
            return {}

        r = self.s.get(base % 'method=init')

        trains = self._get_trains()

        trainno = ''
        #if self.traincode:
        #    try:
        #        trainno = trains[self.traincode]['id']
        #    except KeyError:
        #        pass
        payload = {'orderRequest.train_date': str(self.date),
                   'orderRequest.from_station_telecode': self.fz,
                   'orderRequest.to_station_telecode': self.dz,
                   'orderRequest.train_no': trainno,
                   'trainPassType': 'QB',
                   'trainClass': 'QB#D#Z#T#K#QT#',
                   'includeStudent': '00',
                   'seatTypeAndNum': '',
                   'orderRequest.start_time_str': '00:00--24:00',}
        r = self.s.get(base % 'method=queryLeftTicket', params=payload)
        try:
            t = r.json['datas'].encode('utf-8')
        except TypeError:
            raise TrainQueryError # 上游未返回数据

        result = {}
        count = 1
        for line in t.split(r'\n'):
            text = re.sub(r'<.+?>', '', line).replace('&nbsp;', '')
            text = re.sub(r',无(?=,)', ',0', text).split(',')

            if self.traincode and not text[1] == self.traincode:
                continue

            try:
                tq = '%s(%s->%s)' % (text[1],
                        trains[text[1]]['start'], trains[text[1]]['end'])
            except KeyError:
                tq = text[1]
            try:
                text = [text[0]] + [tq] + [text[2][:-5]] + [text[3][:-5]] + \
                       [text[2][-5:]] + [text[3][-5:]] + text[4:]
            except IndexError:
                continue # TODO: why?

            if ((self.fztc or station_name[text[2]] == self.fz) and
                (self.dztc or station_name[text[3]] == self.dz)):
                result[count] = text[1:]
                count += 1

        return result

    def _get_trains(self):
        if self.date == today:
            tmr = self.date + datetime.timedelta(7)
        else:
            tmr = self.date
        payload = {'date': str(tmr),
                   'fromstation': self.fz,
                   'tostation': self.dz,
                   'starttime': '00:00--24:00',}
        # TODO: switch to base when ready
        #r = self.s.post(base % 'method=queryststrainall', data=payload)
        r = self.s.post('https://www.12306.cn/otsweb/order/querySingleAction.do?method=queryststrainall', data=payload, verify=False)
        tj = r.json
        if not tj:
            return {}
        trains = {}
        for train in tj:
            for code in train['value'].split('/'):
                trains[code] = {'start': train['start_station_name'].encode('utf-8'),
                                'end': train['end_station_name'].encode('utf-8'),
                                'id': train['id'].encode('utf-8')}
        return trains

if __name__ == '__main__':
    tq = TrainQuery('XAY', 'SHH', traincode='', date=today + datetime.timedelta(8))
    data = tq.query()
    for d in sorted(data.keys()):
        print ('%d\t%s' % (d, str(data[d]))).decode("string_escape")
