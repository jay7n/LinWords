#!/usr/bin/python
#--coding:utf-8--

import sys
sys.path.insert(0, './schemes')

import tornado.ioloop
import tornado.web
import word_store as WordStore

from uuid import uuid4
from iciba_collins import ICiBaScheme

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("welcome to my tornado domain!\n")
        #self.write(j)

def _wrap_word(thirdSchema):
    dict = {
        'word' : thirdSchema.GetWord(),
        'definitions' : thirdSchema.GetDefinitions(),
    }
    return dict


class WordHandler(tornado.web.RequestHandler):
    def get(self):
        word_str = self.request.path[1:].split('/')[0]
        word = WordStore.Word(word_str)
        item = word.Get()

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
        (r"/", IndexHandler),
        (r"/[\w\s]+/json", WordHandler),
    ], debug=True)

    app.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
