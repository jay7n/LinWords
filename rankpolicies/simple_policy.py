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
        rank = self.word['rank']
        self.word_store.UpdateWordProperty(self.word, 'rank', rank + 1)

    def RankDown(self):
        if self.word['rank'] > 0:
            rank = self.word['rank']
            self.word_store.UpdateWordProperty(self.word, 'rank', rank - 1)
