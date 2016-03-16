#!/usr/bin/python
# --coding:utf-8--

import json


class BaseDictScheme(object):

    @classmethod
    def GetDictName(cls):
        raise NotImplementedError('Should have implemented this.')

    def GetWord(self):
        raise NotImplementedError('Should have implemented this.')

    def GetPhoneticSymbols(self):
        raise NotImplementedError('Should have implemented this.')

    def GetDefinitions(self):
        raise NotImplementedError('Should have implemented this.')

    def IsValid(self):
        raise NotImplementedError('Should have implemented this.')


class CustomDictSchemeUnit(object):

    def __init__(self, title):
        self._title = title
        self._list = []
        self._map = {}

    def AppendListElem(self, elem):
        self._list.append(elem)

    def AppendMapElem(self, elem_key, elem_value):
        self._map[elem_key] = elem_value

    def GetTitle(self):
        return self._title

    def GetList(self):
        return self._list

    def GetMap(self):
        return self._map

    def Encode(self):
        return {'title': self._title,
                'list': self._list,
                'dict': self._map}

    @classmethod
    def Decode(cls, dict):
        new_ins = cls(dict['title'])
        new_ins._list = dict['list']
        new_ins._dict = dict['dict']
        return new_ins


class BaseDictSchemeUnitParser(object):

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


class DictSchemeParser(object):

    def __init__(self, unit_parser_cls):
        self.unit_parser_cls = unit_parser_cls

    def ParseAllDefinitions(self, definitions):
        return [self.unit_parser_cls.Parse(defi) for defi in definitions]
