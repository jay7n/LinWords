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

import utils.word_helper as word_helper
from dictschemes.iciba_collins_scheme import ICiBaCollinsDictScheme as DictScheme
from wordstores.mongo_store import MongoWordStore as WordStore
from rankpolicies.simple_policy import SimpleRankPolicy as RankPolicy


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
    _wordStore = WordStore(DictScheme.GetDictName())
    # _wordStore.Connect(host='youchun.li', port=27017, db_name='liwords-db')
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

    def _spot_exam(self):
        sort_method = {'field': 'rank', 'direction': -1}
        word = self._wordStore.GetWordBySort(sort_method)
        if word is None:
            msg = 'failed to retrieve an appropriate word as the exam'
            logging.error(msg)
            self.write(msg)

        return word

    def _lookup_word(self, word_literal):
        word = self._wordStore.GetWord(word_literal)
        from_store = word is not None

        if word is None:
            word_scheme = DictScheme(word_literal)
            word = word_helper.pack_word(
                word=word_literal,
                phonetic_sym=word_scheme.GetPhoneticSymbols(),
                definitions=word_scheme.GetDefinitions(),
                rank=0) if word_scheme.IsValid() else None
        else:
            try:
                rank_policy = RankPolicy(word, self._wordStore)
                # since this word has been in the store and now it is asked again,
                # we rank its priority value up
                rank_policy.RankUp()
            except Exception as e:
                word = None
                logging.error(str(e))

        if word is None:
            msg = 'failed to find word \"' + word_literal + '\"'
            logging.error(msg)
            self.write(msg)

        return word, from_store

    def get(self):
        logging.debug('tornado.get!')

        session = {'id': str(uuid.uuid4()),
                   'type': 'lookup_word',  # default to lookup_word
                   'word': None,  # fill this field later
                   'from_store': True  # default to from_store
                   }

        word_literal = self.request.path[1:].split('/')[0]
        word = None

        if word_literal == 'linwords':
            session['type'] = 'spot_exam'
            word = self._spot_exam()
            self._pending_session_queue.append(session['id'], word)
        else:
            word, from_store = self._lookup_word(word_literal)
            if word and not from_store:
                self._pending_session_queue.append(session['id'], word)
                session['from_store'] = False

        if word is None:
            self.set_status(404)
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
        answer_type = self.get_argument('type')
        word = None

        session_id = self.get_argument('session_id')
        if self._pending_session_queue.has_session(session_id):
            word = self._pending_session_queue.get_word(session_id)
            assert word['word'] == word_literal

        if answer_type == 'lookup_word':
            if self.get_argument('store_it') == 'yes':
                if word:
                    try:
                        self._wordStore.AddWord(word)
                        msg = 'the word "' + word_literal + '" has been added into the store.'
                    except RuntimeError as e:
                        msg = str(e)
                else:
                    logging.debug('session "' + session_id +
                                  '" does not exsit. maybe removed due to session timeout ?')
                    msg = 'faied to add word "' + word_literal + '". probably timeout.'
            else:
                msg = 'you deny to add the word "' + word_literal + '" to the store.\n'
                msg += 'bye.'

        elif answer_type == 'spot_exam':
            rank_policy = RankPolicy(word, self._wordStore)
            try:
                if self.get_argument('recognize') == 'yes':
                    rank_policy.RankDown()
                    msg = 'good. this word has been ranked down.'
                else:
                    rank_policy.RankUp()
                    msg = 'well, this word has been ranked up.'
            except Exception as e:
                msg = str(e)

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
