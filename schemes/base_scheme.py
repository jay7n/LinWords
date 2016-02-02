#!/usr/bin/python
#--coding:utf-8--

class BaseWordDictScheme(object):
    def GetSignature(self):
        raise NotImplementedError('Should have implemented this.')

    def GetWord(self):
        raise NotImplementedError('Should have implemented this.')

    def GetDefinitions(self):
        raise NotImplementedError('Should have implemented this.')

class BaseWordDictSchemeUnitParser(object):
    @classmethod
    def Parse(cls, defi):
        raise NotImplementedError('Should have implemented this.')

    def GetWordClass(self):
        raise NotImplementedError('Should have implemented this.')

    def GetEnglishDefi(self):
        raise NotImplementedError('Should have implemented this.')

    def GetChineseDefi(self):
        raise NotImplementedError('Should have implemented this.')

    def GetExamples(self):
        raise NotImplementedError('Should have implemented this.')

class WordDictSchemeParser(object):
    def __init__(self, unit_parser_cls):
        self.unit_parser_cls = unit_parser_cls

    def ParseAllDefinitions(self, definitions):
        return [self.unit_parser_cls.Parse(defi) for defi in definitions]
