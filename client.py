#!/usr/bin/python
#--coding:utf-8--

import requests as req
import json
import sys
sys.path.insert(0, './schemes')
from base_scheme import WordDictSchemeParser
from iciba_collins import ICiBaSchemeUnitParser

_word_dict_parser = WordDictSchemeParser(ICiBaSchemeUnitParser)

def explain_word_and_ask(session_json, path):
    session_dict = json.loads(session_json)
    session_id = session_dict['id']
    word_dict = session_dict['word']

    word = word_dict['word']
    exist = word_dict['exist_in_db']
    definitions = _word_dict_parser.ParseAllDefinitions(word_dict['definitions'])

    print
    print word
    print '---------------------'
    for idx, defi in enumerate(definitions):
        print ''.join([str(idx), '. ', defi.GetWordClass()])
        print ''.join([defi.GetEnglishDefi(), '  ', defi.GetChineseDefi()])

        for key, value in defi.GetExamples().iteritems():
            print '\t' + key
            print '\t' + value
        print

    if not exist:
        res = raw_input('this word hasn\'t been joined in the cache. joined it ? (y/n) ')
        answer = {
        'session_id' : session_id,
        'cache_word' : 'undefined'}

        if res == 'y' or res == 'yes' or res == '':
            answer['cache_word'] = 'yes'
            res = req.post(path, auth=('user', 'pass'), data = answer)

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
            answer['cache_word'] = 'nope'
            res = req.post(path, auth=('user', 'pass'), data = answer)
            print 'bye.'

def main():
    word = sys.argv[1:]
    word = ' '.join(word)

    path ='http://localhost:8000/%s/json' %word
    res = req.get(path, auth=('user', 'pass'))
    if (res.status_code == 200):
        explain_word_and_ask(res.text, path)


if __name__ == '__main__':
    main()
