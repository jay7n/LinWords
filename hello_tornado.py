#!/usr/bin/python
#--coding:utf-8--

import tornado.ioloop
import tornado.web
import json

from bson import json_util as jutil
from pymongo import MongoClient

import html_helper

class MyHandler(tornado.web.RequestHandler):
    def get(self):
        # d = {
        #     'test1' : '我',
        #     'test2' : {
        #         'test2-1' : 'she',
        #         'test2-2' : 'me'
        #     }
        # }
        # j = json.dumps(d)
        self.write("welcome to my tornado domain!\n")
        #self.write(j)

class ThirdPartyWordDictSchema(object):
    def GetWord(self):
        raise NotImplementedError('Should have implemented this.')

    def GetCollinsExplanation(self):
        raise NotImplementedError('Should have implemented this.')

    def GetSimpleChineseExplanation(self):
        raise NotImplementedError('Should have implemented this.')

class ICiBaSchema(ThirdPartyWordDictSchema):
    def __init__(self, word):
        url = 'http://www.iciba.com/' + word
        self._html_content = html_helper.grab_html_content(url)
        self._word = word

    def GetWordItself(self):
        return self._word

    def GetCollinsExplanation(self):
        return self._html_content

    def GetSimpleChineseExplanation(self):
        return None

def _wrap_word(thirdSchema):
    dict = {
        'word' : thirdSchema.GetWord(),
        'collins_explain' : thirdSchema.GetCollinsExplanation(),
        'simplechinese_explain' : thirdSchema.GetSimpleChineseExplanation()
    }

    return dict

class WordExistsExcept(Exception):
    pass

class WordStore(object):
    _db = None

    @classmethod
    def init(cls, host = "youchun.li", port = 27017):
        if not cls._db:
            client = MongoClient(host, port)
            cls._db = client['wordstore-database']
            coll = cls._db['coll']

    def __init__(self):
        WordStore.init()

    def SetWord(self, word):
        coll = self.__class__._db['coll']
        item = coll.find_one({'word' : word})

        if item:
            raise WordExistsExcept

        item = _wrap_word(ICiBaSchema(word))
        coll.insert_one(item)


    def GetWord(self, word):
        coll = self.__class__._db['coll']
        item = coll.find_one({'word' : word})
        if not item:
            item = _wrap_word(ICiBaSchema(word))
            item['exist'] = False
        else:
            item['exist'] = True

        item.pop('_id', None)
        res = jutil.dumps(item)

        '''
            #from http://stackoverflow.com/questions/11094380/python-unicode-string-stored-as-u84b8-u6c7d-u5730-in-file-how-to-convert-it

            s = '\u84b8\u6c7d\u5730'
            print s.decode('unicode-escape')
            # or
            us = unicode(s, 'unicode-escape')
            #--> 蒸汽地
        '''
        return res.decode('unicode-escape')

class WordHandler(tornado.web.RequestHandler):
    def get(self):
        wordStore = WordStore()
        word = self.request.path[1:].split('/')[0]
        res = wordStore.GetWord(word)
        self.write(res)

    def post(self):
        word = self.request.path[1:].split('/')[0]
        try:
            _wordStore.SetWord(word)
        except WordExistsExcept as e:
            self.write('world exists except')

        self.write('success')


if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", MyHandler),
        (r"/[\w\s]+/json", WordHandler),
    ], debug=True)

    app.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
