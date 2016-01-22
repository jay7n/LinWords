#!/usr/bin/python
#--coding:utf-8--

import requests as req
import json
import sys

def explain_word(word_json, path):
    word_dict = json.loads(word_json)
    word = word_dict['word']
    explain = word_dict['explain']
    exist = word_dict['exist']
    print
    print word
    print '---------------------'
    print '1. %s' %explain

    if not exist:
        res = raw_input('this word hasn\'t been joined in the cache. joined it ? (y/n) ')
        if res == 'y' or res == 'yes' or res == '':
            res = req.post(path, auth=('user', 'pass'))
            if res.status_code == 200:
                if res.text == 'success':
                    print 'done.'
                elif res.text == 'world exists except':
                    print 'error: ' + res.text
                else:
                    print 'error: unknown reason'
            else:
                print 'error: status_code:' + str(res.status_code)
        else:
            print 'bye.'

def main():
    word = sys.argv[1:]
    word = ' '.join(word)

    path ='http://localhost:8000/%s/json' %word
    res = req.get(path, auth=('user', 'pass'))
    if (res.status_code == 200):
        explain_word(res.text, path)


if __name__ == '__main__':
    main()
