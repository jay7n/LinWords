#!/usr/bin/python
# --coding:utf-8--

import logging

import pymongo

from wordstores.base_store import BaseWordStore

import utils.word_helper as word_helper


def _validate_word_or_raise(word):
    if word_helper.validate_word(word) is False:
        msg = u'key [\'word\'] for word object %s doesn\'t match type str' % str(word)
        raise Exception(msg)


class MongoWordStore(BaseWordStore):

    def __init__(self, dict_store_name):
        self._dict_store_name = dict_store_name

    def Connect(self, host, port, db_name):
        db_client = pymongo.MongoClient(host, port)
        self._db = db_client[db_name]
        self._dbstore = self._db[self._dict_store_name]

    def AddWord(self, word):
        _validate_word_or_raise(word)

        if self.GetWord(word['word']):
            msg = 'word \"' + word['word'] + \
                '\" already exists. maybe a reentry is exsiting in another \
                session ?'
            raise Exception(msg)

        self._dbstore.insert_one(word)

    def GetWord(self, word_str):
        try:
            word = self._dbstore.find_one({'word': word_str})
            if word:
                word.pop('_id', None)
            return word
        except Exception:
            logging.error('can\'t get access to mongodb via pymongo')
            return None

    def UpdateWord(self, word):
        _validate_word_or_raise(word)

        if self.GetWord(word['word']) is None:
            pass  # TODO
        else:
            self._dbstore.update_one({'word': word['word']}, word)

    def HasWord(self, word_str):
        pass  # TODO

    def RemoveWord(self, word_str):
        pass  # Todo
