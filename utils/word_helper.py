#!/usr/bin/python
# --coding:utf-8--

import logging


def pack_word(word, phonetic_sym, definitions, rank):
    return {
        'word': word,
        'phonetic_sym': phonetic_sym,
        'definitions': definitions,
        'rank': rank
    }


def validate_word(word):
    if type(word) == dict:
        keys = word.keys()
        if 'word' in keys and 'definitions' in keys and 'rank' in keys:
            return True

    return False
