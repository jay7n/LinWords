#!/usr/bin/python
#--coding:utf-8--

class WordStoreInterface(object):
    def AddWord(self, word, scheme_signature):
        raise NotImplementedError('Should have implemented this.')

    def GetWord(self, word_str, scheme_signature):
        raise NotImplementedError('Should have implemented this.')

    def HasWord(self, word_str, scheme_signature):
        raise NotImplementedError('Should have implemented this.')

    def RemoveWord(self, word_str, scheme_signature):
        raise NotImplementedError('Should have implemented this.')

from pymongo import MongoClient
class MongoWordStore(WordStoreInterface):
    def _initdb(self, host = 'youchun.li', port = 27017, db_name = 'liwords-db', collection = 'store'):
        db_client = MongoClient(host, port)
        self._db = db_client[db_name]
        self._dbstore = self._db[collection]

    def __init__(self):
        self._initdb()

    def AddWord(self, word, scheme_signature):
        assert type(word['word']) == str, u'key [\'word\'] for word object %s doesn\'t match type str' %str(word)
        if self.GetWord(word['word'], scheme_signature):
            raise RuntimeError, 'word already exists.'

        word['exist_in_db'] = True
        print word
        self._dbstore.insert_one(word)

    def GetWord(self, word_str, scheme_signature):
        word = self._dbstore.find_one(
            {'word'   : word_str,
             'scheme' : scheme_signature})

        if word:
            word.pop('_id', None)
        return word

    def HasWord(self, word_str, scheme_signature):
        pass # TODO

    def RemoveWord(self, word_str, scheme_signature):
        pass #Todo
