#!/usr/bin/python
#--coding:utf-8--

import tornado.ioloop
import tornado.web
import json

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

def _wrap_word(word):
    dict = {
        'word' : word,
        'explain' : u'test hello 测试'
    }

    return dict

class WordStore(object):
    __db = None

    @classmethod
    def init(cls, host = "youchun.li", port = 27017):
        if not cls.__db:
            from pymongo import MongoClient
            client = MongoClient(host, port)
            cls.__db = client['wordstore-database']
            coll = cls.__db['coll']

    def __init__(self):
        WordStore.init()

    def GetWord(self, word):
        coll = self.__class__.__db['coll']
        item = coll.find_one({'word' : word})
        if not item:
            new_item = _wrap_word(word)
            coll.insert_one(new_item)
            item = new_item

        from bson import json_util as jutil
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

_wordStore = WordStore()

class WordHandler(tornado.web.RequestHandler):
    def get(self):
        word = self.request.path[1:].split('/')[0]

        res = _wordStore.GetWord(word)
        self.write(res)


if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", MyHandler),
        (r"/[\w\s]+/json", WordHandler),
    ])

    app.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
