#!/usr/bin/python
# --coding:utf-8--

from rankpolicies.base_policy import BaseRankPolicy
import utils.word_helper as word_helper


class SimpleRankPolicy(BaseRankPolicy):

    def __init__(self, word, word_store):
        if word_helper.validate_word(word):
            self.word = word
            self.word_store = word_store
        else:
            raise Exception('given word is not a valid object that conforms to the word dict keys')

    def RankUp(self):
        self.word['rank'] += 1
        self.word_store.UpdateWord(self.word)

    def RankDown(self):
        if self.word['rank'] > 0:
            self.word['rank'] -= 1
            self.word_store.UpdateWord(self.word)

    def Query(self, num=1):
        raise NotImplementedError('Should have implemented this.')
