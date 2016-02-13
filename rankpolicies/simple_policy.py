#!/usr/bin/python
# --coding:utf-8--

from rankpolicies.base_policy import BaseRankPolicy


class SimpleRankPolicy(BaseRankPolicy):

    def RankUp(self, word, word_store):
        raise NotImplementedError('Should have implemented this.')

    def RankDown(self, word, word_store):
        raise NotImplementedError('Should have implemented this.')

    def Query(self, num=1):
        raise NotImplementedError('Should have implemented this.')
