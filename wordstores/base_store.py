#!/usr/bin/python
# --coding:utf-8--


class BaseWordStore(object):

    def AddWord(self, word):
        raise NotImplementedError('Should have implemented this.')

    def GetWord(self, word_literal):
        raise NotImplementedError('Should have implemented this.')

    def HasWord(self, word_literal):
        raise NotImplementedError('Should have implemented this.')

    def RemoveWord(self, word_literal):
        raise NotImplementedError('Should have implemented this.')
