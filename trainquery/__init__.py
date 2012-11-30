#!/usr/bin/python2
# vim: set fileencoding=utf-8:

import math
import os
import random
import re
import requests
import tempfile
from datetime import date, timedelta
from station_name import station_name, station_name_rev

class TrainQueryError(Exception):
    pass

class TrainQuery:
    def __init__(self, fz, dz, traincode='',
                 year=date.today().year,
                 month=date.today().month,
                 day=date.today().day):
        self.s = requests.session()
        self.s.config['base_headers']['User-Agent'] = \
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)'
        telecode = lambda z: (station_name.has_key(z.upper()) and
                              (station_name[z.upper()], False) or (z, True))
        self.fz, self.fztc = telecode(fz)
        self.dz, self.dztc = telecode(dz)
        self.traincode = traincode
        zfill = lambda s: str(s).zfill(2)
        self.year = str(year)
        self.month, self.day = [zfill(s) for s in month, day]

    def query(self):
        if (self.fz not in station_name.values() and
            self.dz not in station_name.values()):
            return {}


        r = self.s.get('http://dynamic.12306.cn/otsquery/query/queryRemanentTicketAction.do?method=init')
        payload = {'orderRequest.train_date': '%s-%s-%s' % (self.year, self.month, self.day),
                   'orderRequest.from_station_telecode': station_name_rev[self.fz],
                   'orderRequest.to_station_telecode': station_name_rev[self.dz],
                   'orderRequest.train_no': '', # FIXME: self.traincode,
                   'trainPassType': 'QB',
                   'trainClass': 'QB#D#Z#T#K#QT#',
                   'includeStudent': '00',
                   'seatTypeAndNum': '',
                   'orderRequest.start_time_str': '00:00--24:00',}
        headers = {'Referer': 'http://dynamic.12306.cn/otsquery/query/queryRemanentTicketAction.do?method=init',
                   'X-Requested-With': 'XMLHttpRequest',}
        r = self.s.get('http://dynamic.12306.cn/otsquery/query/queryRemanentTicketAction.do?method=queryLeftTicket', params=payload, headers=headers)
        t = r.json['datas'].encode('utf-8')

        result = {}
        count = 1
        for line in t.split(r'\n'):
            text = re.sub(r'<.+?>', '', line).replace('&nbsp;', '')
            text = re.sub(r',无(?=,)', ',0', text).split(',')
            try:
                text = text[:2] + [text[2][:-5]] + [text[3][:-5]] + [text[2][-5:]] + [text[3][-5:]] + text[4:]
            except IndexError:
                continue # TODO: why?

            if self.traincode and not self.traincode in text[1]:
                continue

            if ((self.fztc or text[2] == self.fz) and
                (self.dztc or text[3] == self.dz)):
                result[count] = text[1:]
                count += 1

        return result


if __name__ == '__main__':
    target = date.today() + timedelta(8)
    tq = TrainQuery('BJP', 'SHH', year=target.year, month=target.month, day=target.day)
    data = tq.query()
    for d in sorted(data.keys()):
        print ('%d\t%s' % (d, str(data[d]))).decode("string_escape")
