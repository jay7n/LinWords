#!/usr/bin/python
#--coding:utf-8--

import sys
sys.path.insert(0, './schemes')

import tornado.ioloop
import tornado.web
import tornado.gen

from uuid import uuid4

from iciba_collins import ICiBaScheme
from word_store import MongoWordStore

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("welcome to my tornado domain!\n")
        #self.write(j)


class WordHandler(tornado.web.RequestHandler):
    _config = {"MaximumWaitResponseSeconds" : 60,           # maximum time to wait for POST response in seconds
               "CheckIntervalSeconds"       : 0.7 }         # interval time to check if POST response is comming in seconds

    class WatingSessionQueue(object):
        def __init__(self):
            self.queue = []

        def append(self, session_id, answer):
            self.queue.append({'session_id' : session_id, 'answer' : answer})

        def get_answer(self, session_id):
            for elm in self.queue:
                if elm['session_id'] == session_id:
                    return elm['answer']

            return None

        def set_answer(self, session_id, answer):
            for elm in self.queue:
                if elm['session_id'] == session_id:
                    elm['answer'] = answer

        def remove(self, session_id):
            for elm in self.queue:
                if elm['session_id'] == session_id:
                    self.queue.remove(elm)
                    break

    _waiting_session_queue = WatingSessionQueue()
    _wordStore = MongoWordStore()

    @staticmethod
    def _wrap_word(third_scheme, scheme_signature):
        wword = {
            'word' : third_scheme.GetWord(),
            'definitions' : third_scheme.GetDefinitions(),
            'scheme_signature' : third_scheme.GetSignature(),
            'exist_in_db' : False
        }
        return wword

    @tornado.gen.coroutine
    def get(self):
        word_str = self.request.path[1:].split('/')[0]
        word = _wordStore.GetWord(word_str, ICiBaScheme.GetSignature())

        session = {
            'id' : uuid4(),
            'word' : None
        }
        waiting_session = None

        had_word = False if word == None else True

        if not had_word:
            word = self.__class__._wrap_word(ICiBaScheme(word_str))
            self.__class__._waiting_session_queue.append(session['id'], 'undefined')

        session['word'] = word

        res = jutil.dumps(session)

        '''
            #from http://stackoverflow.com/questions/11094380/python-unicode-string-stored-as-u84b8-u6c7d-u5730-in-file-how-to-convert-it
            s = '\u84b8\u6c7d\u5730'
            print s.decode('unicode-escape')
            # or
            us = unicode(s, 'unicode-escape')
            #--> 蒸汽地
        '''
        self.write(res.decode('unicode-escape'))

        if not had_word:
            config = self.__class__._config
            check_interval = config['CheckIntervalSeconds']
            for_loop_count = int(round(config['MaximumWaitPOSTSeconds'] / check_interval))

            answer = None
            for i in xrange(for_loop_count):
                answer = self._waiting_session_queue.get_answer(session['id'])
                if answer == 'undefined':
                    yield tornado.gen.sleep(check_interval)
                else:
                    break

            if answer == 'yes':
                try:
                    wordStore.AddWord(word)
                except RuntimeError as e:
                    self.write(str(e))

            self.__calss__._waiting_session_queue.remove(session['id'])

    @tornado.gen.coroutine
    def post(self):
        answer = self.get_argument('cache_word')
        self.__class__._waiting_session_queue.set_answer(answer)
        yield tornado.gen.sleep(0.7)

        word_str = self.request.path[1:].split('/')[0]
        if _wordStore.HasWord(word_str, ICiBaScheme.GetSignature()):

        self.write(word + ': added successfully')

if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/[\w\s]+/json", WordHandler),
    ], debug=True)

    app.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
