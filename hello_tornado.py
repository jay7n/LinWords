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

class WordHandler(tornado.web.RequestHandler):
    def get(self):
        word = self.request.path[1:]
        self.write(word)
        self.write("女孩")

if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/", MyHandler),
        (r"/[\w\s]+", WordHandler),
    ])

    app.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
