#!/usr/bin/python
#--coding:utf-8--

import tornado.ioloop
import tornado.web
import json

from bson import json_util as jutil
from pymongo import MongoClient
from uuid import uuid4

import sys
sys.path.insert(0, './schemes')
from iciba_collins import ICiBaScheme

class MyHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("welcome to my tornado domain!\n")
        #self.write(j)


def _wrap_word(thirdSchema):
    dict = {
        'word' : thirdSchema.GetWord(),
        'definitions' : thirdSchema.GetDefinitions(),
    }
    return dict

class WordExistsExcept(Exception):
    pass

class WordStore(object):
    _db = None

    @classmethod
    def init(cls, host = "youchun.li", port = 27017):
        if not cls._db:
            db_client = MongoClient(host, port)
            cls._db = db_client['wordstore-database']
            coll = cls._db['coll']

    def __init__(self):
        WordStore.init()

    def SetWord(self, word):
        coll = self.__class__._db['coll']
        item = coll.find_one({'word' : word})

        if item:
            raise WordExistsExcept

        item = _wrap_word(ICiBaScheme(word))
        coll.insert_one(item)

    def GetWord(self, word):
        coll = self.__class__._db['coll']
        item = coll.find_one({'word' : word})
        if not item:
            item = _wrap_word(ICiBaScheme(word))
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
        wordStore = WordStore()

        try:
            wordStore.SetWord(word)
        except WordExistsExcept as e:
            self.write(word + ' : already exists')

        self.write(word + ': added successfully')


if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", MyHandler),
        (r"/[\w\s]+/json", WordHandler),
    ], debug=True)

    app.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
