#!/usr/bin/python
# --coding:utf-8--

import sys

import requests
import json
import logging

from dictschemes.base_scheme import DictSchemeParser
from dictschemes.iciba_collins_scheme import ICiBaCollinsSchemeUnitParser as SchemeUnitParser

logging.basicConfig(level=logging.DEBUG)

_word_dict_parser = DictSchemeParser(SchemeUnitParser)


def print_definitions(word, phonetic_sym_list, definitions):
    print
    print word + '  ' + ', '.join(phonetic_sym_list)
    print '---------------------'
    for idx, defi in enumerate(definitions):
        if defi.IsOfCustom():
            custom = defi.GetCustom()
            title = custom.GetTitle()

            if title is not None:
                print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
                print title
                print

                for list_elem in custom.GetList():
                    print '\t' + list_elem
                    print

                for elem_key, elem_value in custom.GetMap().iteritems():
                    print '\t' + elem_key + ':'
                    print '\t\t' + elem_value
                    print

                print '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'

            print

        else:
            print ''.join([str(idx), '. ', defi.GetWordClass()])
            print ''.join([defi.GetEnglishDefi(), '  ', defi.GetChineseDefi()])

            for elm in defi.GetExamples():
                print '\t' + elm['en_eg']
                print '\t' + elm['cn_eg']
                print

            print


def explain_word_and_ask(session_json, path):
    session_dict = json.loads(session_json)
    session_id = session_dict['id']
    logging.debug(session_id)

    session_type = session_dict['type']
    word_dict = session_dict['word']
    from_store = session_dict['from_store']

    word = word_dict['word']
    phonetic_sym = word_dict['phonetic_sym']
    definitions = _word_dict_parser.ParseAllDefinitions(word_dict['definitions'])
    answer = {'session_id': session_id, 'word': word,
              'type': session_type, 'store_it': 'nope', 'recognize': 'nope'}
    res = None

    if session_type == 'lookup_word':
        print_definitions(word, phonetic_sym, definitions)

        if not from_store:
            res = raw_input('this word hasn\'t been added in the store. add it ? (y/n) ')

            if res == 'y' or res == 'yes' or res == '':
                answer['store_it'] = 'yes'

            res = requests.post(path, auth=('user', 'pass'), data=answer)
        else:
            answer = None

    elif session_type == 'spot_exam':
        print word
        print
        res = raw_input('do you recognize this word ? ')

        if res == 'y' or res == 'yes':
            answer['recognize'] = 'yes'
        else:
            print_definitions(word, definitions)

    if answer is not None:
        res = requests.post(path, auth=('user', 'pass'), data=answer)
        if res.status_code == 200:
            print res.text
        else:
            print 'error: status_code:' + str(res.status_code)


def main():
    word = ' '.join(sys.argv[1:])
    if word == '':  # empty str means no extra args
        word = 'linwords'

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
