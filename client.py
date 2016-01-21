#!/usr/bin/python
#--coding:utf-8--

import requests as req

r = req.get('http://localhost:8080/girl', auth=('user', 'pass'))

if (r.status_code == 200):
    print r.text
