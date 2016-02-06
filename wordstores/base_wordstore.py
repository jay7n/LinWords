#!/usr/bin/python
# --coding:utf-8--


class WordStoreInterface(object):

    def AddWord(self, word):
        raise NotImplementedError('Should have implemented this.')

    def GetWord(self, word_str):
        raise NotImplementedError('Should have implemented this.')

    def HasWord(self, word_str):
        raise NotImplementedError('Should have implemented this.')

    def RemoveWord(self, word_str):
        raise NotImplementedError('Should have implemented this.')
