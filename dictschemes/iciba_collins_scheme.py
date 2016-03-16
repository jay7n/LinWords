#!/usr/bin/python
# --coding:utf-8--

import logging
import bs4

from dictschemes.base_scheme import BaseDictScheme
from dictschemes.base_scheme import CustomDictSchemeUnit
from dictschemes.base_scheme import BaseDictSchemeUnitParser

import utils.html_helper as html_helper


class ICiBaCollinsDictScheme(BaseDictScheme):

    @classmethod
    def GetDictName(cls):
        return "ICiBaScheme_Collins"

    def _parseTextParagraph(self, text_paragraph):
        try:
            tp = text_paragraph

            title = tp.find(class_='pragraph-h family-english size-english').text
            res = CustomDictSchemeUnit(title)

            en_item = tp.find(class_='p-english').text
            cn_item = tp.find(class_='p-chinese family-chinese size-chinese size-chinese').text
            res.AppendListElem(en_item)
            res.AppendListElem(cn_item)

            res = res.Encode()
            res['type'] = 'custom'
            return res

        except Exception as e:
            logging.error(str(e))
            return None

    def _parseSuggestion(self, suggestion):
        try:
            su = suggestion
            sug_items = su.find_all(class_='sug-text')

            res = CustomDictSchemeUnit('Suggest')

            for item in sug_items:
                res.AppendListElem(item.text)

            res = res.Encode()
            res['type'] = 'custom'
            return res

        except Exception as e:
            logging.error(str(e))
            return None

    def _parseSectionPrep(self, section_prep):
        try:
            sp = section_prep

            res = {}
            res['type'] = 'normal'
            res['word class'] = sp.find(class_='family-english').text
            res['english defi'] = sp.find(class_='family-english size-english prep-en').text
            res['chinese defi'] = sp.find(class_='family-chinese').text
            res_examples = []

            example_sentences = sp.find(class_='text-sentence').find_all(class_='sentence-item')
            for example in example_sentences:
                en_eg = example.find(class_='family-english').text
                cn_eg = example.find(class_='family-chinese').text

                res_examples.append({'en_eg': en_eg, 'cn_eg': cn_eg})

            res['examples'] = res_examples
            return res

        except Exception as e:
            logging.error(str(e))
            return None  # we do not handle anything here, just in case crash

    def _parseHtmlContent(self, html_content):
        if not html_content:
            return

        phonetics = []
        soup = bs4.BeautifulSoup(html_content, "html.parser")
        base_speak_tag = soup.find(class_='base-speak')
        try:
            bs = base_speak_tag
            spans = bs.find_all(name='span')
            for span in spans:
                phonetics.append(span.text)
        except Exception as e:
            logging.error(str(e))
            logging.warning(
                'failed to locate the phonetic symbol for the word \'' + self.word + '\'')

        collins_tag = soup.find(name='li', text=u'柯林斯高阶英汉双解学习词典')
        collins_tag = collins_tag.parent.next_sibling.next_sibling
        collins_section_preps = collins_tag.find(
            class_='collins-section').find_all(class_='section-prep')

        definitions = []
        for section_prep in collins_section_preps:
            defi = None

            tp = section_prep.find(class_='text-paragraph')
            if tp is not None:
                defi = self._parseTextParagraph(tp)
                if defi is not None:
                    definitions.append(defi)

            su = section_prep.find(class_='suggest')
            if su is not None:
                defi = self._parseSuggestion(su)
                if defi is not None:
                    definitions.append(defi)

            defi = self._parseSectionPrep(section_prep)
            if defi is not None:
                definitions.append(defi)

        return phonetics, definitions

    def __init__(self, word):
        try:
            self.word = word
            self.valid = True
            self.phonetics = []

            url = 'http://www.iciba.com/' + word
            html_content = html_helper.grab_html_content(url)
            self.phonetics, self.definitions = self._parseHtmlContent(html_content)
        except Exception as e:
            logging.error(str(e))
            self.word = None
            self.valid = False
            self.definitions = None
            self.phonetics = None

    def GetWord(self):
        return self.word

    def GetPhoneticSymbols(self):
        return self.phonetics

    def GetDefinitions(self):
        return self.definitions

    def IsValid(self):
        return self.valid


class ICiBaCollinsSchemeUnitParser(BaseDictSchemeUnitParser):

    @classmethod
    def Parse(cls, defi):
        ins = cls()

        if defi['type'] == 'normal':
            wc = defi['word class']
            ed = defi['english defi']
            cd = defi['chinese defi']
            eg = defi['examples']
            ins._setForNormal(wc, ed, cd, eg)

        elif defi['type'] == 'custom':
            ins._setForCustom(defi)

        return ins

    def _setForNormal(self, word_class, english_defi, chinese_defi, examples):
        self.word_class = word_class
        self.english_defi = english_defi
        self.chinese_defi = chinese_defi
        self.examples = examples

        self.custom = None

    def _setForCustom(self, custom):
        self.custom = CustomDictSchemeUnit.Decode(custom)

        self.word_class = self.english_defi = self.chinese_defi = self.examples = None

    def IsOfCustom(self):
        return self.custom is not None

    def GetWordClass(self):
        return self.word_class

    def GetEnglishDefi(self):
        return self.english_defi

    def GetChineseDefi(self):
        return self.chinese_defi

    def GetExamples(self):
        return self.examples

    def GetCustom(self):
        return self.custom
