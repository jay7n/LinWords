#!/usr/bin/python
#--coding:utf-8--

from bson import json_util as jutil
from pymongo import MongoClient

import sys

class WordExistsExcept(Exception):
    pass

class WordStoreInterface(object):
    def AddWord(self, word_str):
        raise NotImplementedError('Should have implemented this.')

    def GetWord(self, word_str):
        raise NotImplementedError('Should have implemented this.')

    def RemoveWord(self, word_str):
        raise NotImplementedError('Should have implemented this.')

class MongoWordStore(WordStoreInterface):
    def _initdb(self host = 'youchun.li', port = 27017, db_name = 'liwords-db', collection = 'store'):
        if not self._db:
            db_client = MongoClient(host, port)
            self._db = db_client[db_name]
            self._dbstore = self._db[collection]

    def __init__(self):
        self._initdb()

    def AddWord(self, word):
        assert type(word['word']) == str, u'key [\'word\'] for word object %s doesn\'t match type str' %str(word)
        self._dbstore.insert_one(word)

    def GetWord(self, word_liter):
        word = self._dbstore.find_one({'word' : word_liter})
        return word

    def RemoveWord(self, word_str):
        pass #todo
