#!/usr/bin/python
#--coding:utf-8--

class WordStoreInterface(object):
    def AddWord(self, word):
        raise NotImplementedError('Should have implemented this.')

    def GetWord(self, word_str):
        raise NotImplementedError('Should have implemented this.')

    def HasWord(self, word_str):
        raise NotImplementedError('Should have implemented this.')

    def RemoveWord(self, word_str):
        raise NotImplementedError('Should have implemented this.')

from pymongo import MongoClient
class MongoWordStore(WordStoreInterface):
    def __init__(self, dict_store_name):
        self._dict_store_name = dict_store_name

    def Connect(self, host, port, db_name):
        db_client = MongoClient(host, port)
        self._db = db_client[db_name]
        self._dbstore = self._db[self._dict_store_name]

    def AddWord(self, word):
        assert type(word['word']) == str, u'key [\'word\'] for word object %s doesn\'t match type str' %str(word)
        if self.GetWord(word['word']):
            msg = 'word \"' + word['word'] + '\" already exists. maybe a reentry is exsiting in another session ?'
            raise RuntimeError, msg

        word['exist_in_db'] = True
        self._dbstore.insert_one(word)

    def GetWord(self, word_str):
        word = self._dbstore.find_one({'word'   : word_str })
        if word:
            word.pop('_id', None)

        return word

    def HasWord(self, word_str):
        pass # TODO

    def RemoveWord(self, word_str):
        pass #Todo
