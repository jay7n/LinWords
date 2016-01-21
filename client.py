#!/usr/bin/python
#--coding:utf-8--

import requests as req
import json
import sys

def explain_word(word_json):
    word_dict = json.loads(word_json)
    word = word_dict['word']
    explain = word_dict['explain']
    print
    print word
    print '---------------------'
    print '1. %s' %explain

def main():
    words = sys.argv[1:]

    for word in words:
        url ='http://localhost:8000/%s/json' %word
        r = req.get(url, auth=('user', 'pass'))
        if (r.status_code == 200):
            explain_word(r.text)


if __name__ == '__main__':
    main()
