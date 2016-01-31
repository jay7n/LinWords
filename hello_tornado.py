#!/usr/bin/python
#--coding:utf-8--

import sys
sys.path.insert(0, './schemes')

import tornado.ioloop
import tornado.web
import tornado.gen
import time
import uuid
import json

from iciba_collins import ICiBaScheme
from word_store import MongoWordStore
from bson import json_util as jutil

class PendingSessionQueue(object):
    def __init__(self):
        self.queue = []

    # def append(self, session_id, answer):
    #     self.queue.append({
    #         'session_id' : session_id,
    #         # 'answer' : answer,
    #         'timestamp' : time.time()})
    def append(self, session_id, word):
        print "word " + word['word'] + " added"
        print "append.session_id= " + session_id
        self.queue.append({
            'session_id' : session_id,
            'word' : word,
            'timestamp' : time.time()})

    def has_session(self, session_id):
        print "has_session.session_id= " + session_id
        for s in self.queue:
            print 's.session_d= ' + s['session_id']
            if s['session_id'] == session_id:
                return True

        return False

    def remove_session(self, session_id):
        print 'remove_session'
        for s in self.queue:
            if s['session_id'] == session_id:
                self.queue.remove(s)
                return True

        return False

    def get_word(self, session_id):
        for s in self.queue:
            if s['session_id'] == session_id:
                return s['word']

    # def get_answer(self, session_id):
    #     for elm in self.queue:
    #         if elm['session_id'] == session_id:
    #             return elm['answer']
    #
    #     return None

    # def set_answer(self, session_id, answer):
    #     for elm in self.queue:
    #         if elm['session_id'] == session_id:
    #             elm['answer'] = answer

    def remove_timeout_session(self, lifetime):
        print 'remove_timeout_session'
        # if (len(self.queue) > 0):
        #     new_queue = [s for s in self.queue if time.time() - s['timestamp'] < lifetime]
        #     self.queue = new_queue

class WordHandler(tornado.web.RequestHandler):
    _pending_session_queue = PendingSessionQueue()
    _wordStore = MongoWordStore()

    def __init__(self, application, request, **kwargs):
        super(WordHandler, self).__init__(application, request, **kwargs)

        self._config = {'PendingSesionLifetime'       : 60,          # maximum time to wait for POST response in seconds
                        'ScanPendingSessionInternval' : 30 }         # interval time to check if POST response is comming in seconds


        print "WordHandler init"
        scan_interval = self._config['ScanPendingSessionInternval']
        tornado.ioloop.PeriodicCallback(self._polling, scan_interval*1000).start()

    def _polling(self):
        pending_session_life_time = self._config['PendingSesionLifetime']
        self._pending_session_queue.remove_timeout_session(pending_session_life_time)
        print "polling!"

    def _wrap_word(self, third_scheme):
        wword = {
            'word' : third_scheme.GetWord(),
            'definitions' : third_scheme.GetDefinitions(),
            'scheme_signature' : third_scheme.GetSignature(),
            'exist_in_db' : False
        }
        return wword

    def get(self):
        print "tornado.get!"
        session = {'id' : str(uuid.uuid4()), 'word' : None}

        word_str = self.request.path[1:].split('/')[0]
        word = self._wordStore.GetWord(word_str, ICiBaScheme.GetSignature())

        if not word:
            word = self._wrap_word(ICiBaScheme(word_str))
            self._pending_session_queue.append(session['id'], word)

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

    def post(self):
        print "tornado.post!"
        cache_word = self.get_argument('cache_word')
        session_id = self.get_argument('session_id')
        if self._pending_session_queue.has_session(session_id):
            word = self._pending_session_queue.get_word(session_id)
            if cache_word == 'yes':
                try:
                    self._wordStore.AddWord(word, ICiBaScheme.GetSignature())
                    self.write(word['word'] + ": added successfully")
                except RuntimeError as e:
                    self.write(str(e))
            else:
                print "yo're deny to add this word. got it"
                self.write("yo're deny to add this word. got it")
                pass # TODO
        else:
            print "now session found"
            pass #TODO

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("welcome to my tornado domain!\n")
        #self.write(j)

if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/[\w\s]+/json", WordHandler),
    ], debug=True)

    app.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
