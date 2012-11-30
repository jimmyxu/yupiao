#!/usr/bin/python2
# vim: set fileencoding=utf-8:

import math
import os
import random
import re
import requests
import tempfile
from datetime import date, timedelta
from ocr import OCR
from station_name import station_name

tmpdir = '/home/jimmy/src/trainquery/ocr/img/'

class TrainQueryError(Exception):
    pass

class TrainQuery:
    def __init__(self, fz, dz, traincode='',
                 month=date.today().month, day=date.today().day):
        self.s = requests.session()
        self.s.config['base_headers']['User-Agent'] = \
            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)'
        telecode = lambda z: (station_name.has_key(z.upper()) and
                              (station_name[z.upper()], False) or (z, True))
        self.fz, self.fztc = telecode(fz)
        self.dz, self.dztc = telecode(dz)
        self.traincode = traincode
        zfill = lambda s: str(s).zfill(2)
        self.month, self.day = [zfill(s) for s in month, day]

    def query(self):
        if (self.fz not in station_name.values() and
            self.dz not in station_name.values()):
            return {}


        r = self.s.get('http://dynamic.12306.cn/TrainQuery/leftTicketByStation.jsp')
        ict, ictval = re.search(r'<input type="hidden" id="(.+?)" name="\1" value="(.+?)"/>', r.text.encode('utf-8')).groups()
        captcha = self._do_ocr()
        payload = {ict: ictval,
                   'fdl': '',
                   'lx': '00',
                   'nmonth3': self.month,
                   'nmonth3_new_value': 'false',
                   'nday3': self.day,
                   'nday3_new_value': 'false',
                   'startStation_ticketLeft': self._alert(self.fz),
                   'startStation_ticketLeft_new_value': 'false',
                   'arriveStation_ticketLeft': self._alert(self.dz),
                   'arriveStation_ticketLeft_new_value': 'false',
                   'trainCode': self.traincode,
                   'trainCode_new_value': 'false',
                   'rFlag': 1,
                   'name_ckball': 'value_ckball',
                   'tFlagDC': 'DC',
                   'tFlagZ': 'Z',
                   'tFlagT': 'T',
                   'tFlagK': 'K',
                   'tFlagPK': 'PK',
                   'tFlagPKE': 'PKE',
                   'tFlagLK': 'LK',
                   'randCode': captcha}
        r = self.s.post('http://dynamic.12306.cn/TrainQuery/iframeLeftTicketByStation.jsp', data=payload)

        t = r.text.encode('utf-8')
        if t.find('当前页面的验证码已过期') != -1:
            raise TrainQueryError # 验证码已过期

        result = {}
        count = 1
        for line in t.split('\n'):
            if not line.startswith('parent.mygrid.addRow('):
                continue
            try:
                text = re.match(r'parent\.mygrid\.addRow\(\d+,"(.+?)",\d+\);', line).group(1)
                text = [i.split('^')[0] for i in text.split(',')]

                if ((self.fztc or text[2] == self.fz) and
                    (self.dztc or text[3] == self.dz)):
                    result[count] = text[1:]
                    count += 1
            except AttributeError:
                raise TrainQueryError # 结果行不合法

        return result


    def _get_captcha(self, fd):
        with os.fdopen(fd[0], 'wb') as f:
            captcha = self.s.get('http://dynamic.12306.cn/TrainQuery/passCodeActi0n.do?rand=rrand')
            if captcha.status_code != requests.codes.ok:
                raise TrainQueryError # 验证码获取失败
            f.write(captcha.content)

    def _do_ocr(self):
        fd = tempfile.mkstemp(suffix='.jpg', dir=tmpdir)
        try:
            self._get_captcha(fd)
            o = OCR(fd[1])
            #o._print()
        finally:
            os.unlink(fd[1])
        return o.ocr()

    def _alert(self, s, pwd='liusheng'):
        s = s.decode('utf-8')
        prand = ""
        for i in xrange(len(pwd)):
            prand += str(ord(pwd[i]))

        sPos = len(prand) / 5
        mult = int(prand[sPos] + prand[sPos * 2] + prand[sPos * 3] + prand[sPos * 4] + prand[sPos * 5])
        incr = int(math.ceil(len(pwd) / 2.0))
        modu = (2 ** 31) - 1

        salt = int(round(random.random() * 1000000000)) % 100000000
        prand += str(salt)

        prand = (mult * len(prand) + incr) % modu
        enc_chr = ""
        enc_str = ""

        for i in xrange(len(s)):
            enc_chr = int(ord(s[i]) ^ int(math.floor((float(prand) / modu) * 255)))
            if enc_chr < 16:
                enc_str += "0" + hex(enc_chr)[2:]
            else:
                enc_str += hex(enc_chr)[2:]
            prand = (mult * prand + incr) % modu

        salt = hex(salt)[2:]
        while len(salt) < 8:
            salt = "0" + salt
        enc_str += salt

        return enc_str


if __name__ == '__main__':
    target = date.today() + timedelta(8)
    tq = TrainQuery('BJP', 'SHH', month=target.month, day=target.day)
    data = tq.query()
    for d in sorted(data.keys()):
        print ('%d\t%s' % (d, str(data[d]))).decode("string_escape")
