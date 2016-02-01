#!/usr/bin/python
#--coding:utf-8--

import html_helper

from bs4 import BeautifulSoup
from base_scheme import BaseWordDictScheme
from base_scheme import BaseWordDictSchemeUnitParser

class ICiBaScheme(BaseWordDictScheme):
    @classmethod
    def GetSignature(cls):
        return "ICiBaScheme_Collins"

    def _parseCollinsSectionPrep(self, section_prep):
        sp = section_prep

        # We didn't handle 'Suggestions' for now
        if sp.find(class_='suggest'):
            return None

        res = {}
        res['word class'] = sp.find(class_='family-english').text
        res['english defi'] = sp.find(class_='family-english size-english prep-en').text
        res['chinese defi'] = sp.find(class_='family-chinese').text
        res_examples = []

        example_sentences = sp.find(class_='text-sentence').find_all(class_='sentence-item')
        for example in example_sentences:
            en_eg = example.find(class_='family-english').text
            cn_eg = example.find(class_='family-chinese').text

            res_examples.append({'en_eg' : en_eg, 'cn_eg' : cn_eg})

        res['examples'] = res_examples
        return res

    def _parseHtmlContent(self, html_content):
        if not html_content:
            return

        soup = BeautifulSoup(html_content, "html.parser")
        collins_tag = soup.find(name='li', text=u'柯林斯高阶英汉双解学习词典').parent.next_sibling.next_sibling
        collins_section_preps = collins_tag.find(class_='collins-section').find_all(class_='section-prep')

        definitions = []
        for section_prep in collins_section_preps:
            defi = self._parseCollinsSectionPrep(section_prep)
            if defi:
                definitions.append(defi)

        return definitions

    def __init__(self, word):
        url = 'http://www.iciba.com/' + word
        html_content = html_helper.grab_html_content(url)
        self.definitions = self._parseHtmlContent(html_content)
        self.word = word

    def GetWord(self):
        return self.word

    def GetDefinitions(self):
        return self.definitions


class ICiBaSchemeUnitParser(BaseWordDictSchemeUnitParser):
    @classmethod
    def Parse(cls, defi):
        wc = defi['word class']
        ed = defi['english defi']
        cd = defi['chinese defi']
        eg = defi['examples']

        return cls(wc, ed, cd, eg)

    def __init__(self, word_class, english_defi, chinese_defi, examples):
        self.word_class = word_class
        self.english_defi = english_defi
        self.chinese_defi = chinese_defi
        self.examples = examples

    def GetWordClass(self):
        return self.word_class

    def GetEnglishDefi(self):
        return self.english_defi

    def GetChineseDefi(self):
        return self.chinese_defi

    def GetExamples(self):
        return self.examples
