#!/usr/bin/python
# --coding:utf-8--

import logging

import wordstores.base_store as base_word_store
import pymongo


class MongoWordStore(base_word_store.BaseWordStore):

    def __init__(self, dict_store_name):
        self._dict_store_name = dict_store_name

    def Connect(self, host, port, db_name):
        db_client = pymongo.MongoClient(host, port)
        self._db = db_client[db_name]
        self._dbstore = self._db[self._dict_store_name]

    def AddWord(self, word):
        assert type(
            word['word']) == str, u'key [\'word\'] for word object %s doesn\'t \
            match type str' % str(word)
        if self.GetWord(word['word']):
            msg = 'word \"' + word['word'] + \
                '\" already exists. maybe a reentry is exsiting in another \
                session ?'
            raise RuntimeError(msg)

        word['exist_in_db'] = True
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

    def HasWord(self, word_str):
        pass  # TODO

    def RemoveWord(self, word_str):
        pass  # Todo
