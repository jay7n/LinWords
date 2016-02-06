#!/usr/bin/python
# --coding:utf-8--

import sys
import time
import uuid
import json
import logging

import tornado.ioloop
import tornado.web
import tornado.gen
from bson import json_util as jutil

import schemes.iciba_collins as scheme
import wordstores.mongo_wordstore as wordstore

logging.basicConfig(level=logging.DEBUG)


class PendingSessionQueue(object):

    def __init__(self):
        self.queue = []

    def append(self, session_id, word):
        logging.debug('word "' + word['word'] +
                      '" added into pending sessions and waiting for response... ')

        self.queue.append({
            'session_id': session_id,
            'word': word,
            'timestamp': time.time()})

    def has_session(self, session_id):
        for s in self.queue:
            if s['session_id'] == session_id:
                return True

        return False

    def remove_session(self, session_id):
        logging.debug('remove_session')

        for s in self.queue:
            if s['session_id'] == session_id:
                self.queue.remove(s)
                return True

        return False

    def get_word(self, session_id):
        for s in self.queue:
            if s['session_id'] == session_id:
                return s['word']

    def remove_timeout_session(self, lifetime):
        if (len(self.queue) > 0):
            new_queue = [s for s in self.queue if time.time() - s['timestamp'] < lifetime]

            excluded = [s for s in self.queue if s not in new_queue]
            for excl in excluded:
                logging.debug('word "' + excl['word']['word'] +
                              '" has been removed from pending sessions')

            self.queue = new_queue


class WordHandler(tornado.web.RequestHandler):
    _pending_session_queue = PendingSessionQueue()
    _wordStore = wordstore.MongoWordStore(scheme.ICiBaScheme.GetDictName())
    # _wordStore.Connect(host = 'youchun.li', port = 27017, db_name = 'liwords-db')
    _wordStore.Connect(host='localhost', port=27017, db_name='liwords-db')

    def __init__(self, application, request, **kwargs):
        super(WordHandler, self).__init__(application, request, **kwargs)

        self._config = {'PendingSesionLifetime': 60,          # maximum time to wait for POST response in seconds
                        'ScanPendingSessionInternval': 30}         # interval time to check if POST response is comming in seconds

        logging.debug('WordHandler init')
        scan_interval = self._config['ScanPendingSessionInternval']
        tornado.ioloop.PeriodicCallback(self._polling, scan_interval * 1000).start()

    def _polling(self):
        logging.debug('polling!')
        pending_session_life_time = self._config['PendingSesionLifetime']
        self._pending_session_queue.remove_timeout_session(pending_session_life_time)

    def _wrap_word(self, third_scheme):
        if third_scheme.IsValid():
            wword = {
                'word': third_scheme.GetWord(),
                'definitions': third_scheme.GetDefinitions(),
                'exist_in_db': False
            }
            return wword

        return None

    def get(self):
        logging.debug('tornado.get!')
        session = {'id': str(uuid.uuid4()), 'word': None}

        word_literal = self.request.path[1:].split('/')[0]
        word = self._wordStore.GetWord(word_literal)

        if not word:
            word = self._wrap_word(scheme.ICiBaScheme(word_literal))
            if word is not None:
                self._pending_session_queue.append(session['id'], word)

        if word is None:
            msg = 'failed to find word \"' + word_literal + '\"'
            logging.warning(msg)

            self.set_status(404)
            self.write(msg)
            return

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
        msg = ''
        word_literal = self.get_argument('word')

        if self.get_argument('cache_it') == 'yes':
            session_id = self.get_argument('session_id')
            if self._pending_session_queue.has_session(session_id):
                word = self._pending_session_queue.get_word(session_id)
                assert word['word'] == word_literal
                try:
                    self._wordStore.AddWord(word)
                    msg = 'the word "' + word_literal + '" has been cached.'
                except RuntimeError as e:
                    msg = str(e)
            else:
                logging.debug('session "' + session_id +
                              '" does not exsit. maybe removed due to session timeout ?')
                msg = 'faied to add word "' + word_literal + '". probably timeout.'
        else:
            msg = 'you deny to cache the word "' + word_literal + '". \nbye.'

        msg_type = type(msg)
        assert msg_type == str or msg_type == unicode, 'error: msg is not a str/unicode type!'

        self.write(msg)


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("welcome to my tornado domain!\n")

if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/[\w\s]+/json", WordHandler),
    ], debug=True)

    app.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
