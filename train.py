#!/usr/bin/python2
# vim: set fileencoding=utf-8:

import cgi
import json
import os
import requests
import trainquery.station_name as station_name

url = 'http://yupiao.info/api/train/%s' % os.getenv('REQUEST_URI').split('/train/', 1)[1]
r = requests.get(url)

print 'Content-Type: %s\n\n' % r.headers['content-type']

j = r.json()
for station in j['stop'].keys():
    try:
        j['stop'][station_name[station.encode('utf-8')]] = j['stop'][station]
    except KeyError:
        pass

print json.dumps(j)
