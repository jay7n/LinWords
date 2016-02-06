#!/usr/bin/python
# --coding:utf-8--

import sys

import requests
import json
import logging

import schemes.base_scheme as base_scheme
import schemes.iciba_collins as iciba_collins

logging.basicConfig(level=logging.DEBUG)

_word_dict_parser = base_scheme.WordDictSchemeParser(iciba_collins.ICiBaSchemeUnitParser)


def explain_word_and_ask(session_json, path):
    session_dict = json.loads(session_json)
    session_id = session_dict['id']
    logging.debug(session_id)
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

        for elm in defi.GetExamples():
            print '\t' + elm['en_eg']
            print '\t' + elm['cn_eg']

        print

    if not exist:
        res = raw_input('this word hasn\'t been joined in the cache. joined it ? (y/n) ')

        answer = {'session_id': session_id, 'word': word, 'cache_it': 'undefined'}

        if res == 'y' or res == 'yes' or res == '':
            answer['cache_it'] = 'yes'
            res = requests.post(path, auth=('user', 'pass'), data=answer)

            if res.status_code == 200:
                print res.text
            else:
                print 'error: status_code:' + str(res.status_code)
        else:
            answer['cache_it'] = 'nope'
            res = requests.post(path, auth=('user', 'pass'), data=answer)
            print res.text


def main():
    word = sys.argv[1:]
    word = ' '.join(word)

    path = 'http://localhost:8000/%s/json' % word
    try:
        res = requests.get(path, auth=('user', 'pass'))
        if res:
            if (res.status_code == 200):
                explain_word_and_ask(res.text, path)
            else:
                print res.text
    except requests.exceptions.ConnectionError:
        print 'failed to connect to server \"' + path + '\"'
        print 'did you open the server correctly ?'

if __name__ == '__main__':
    main()
