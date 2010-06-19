# -*- coding: utf-8 -*-

import tornado.web
import tornado.ioloop
import time
from agatsuma.core import Core
from agatsuma import Settings
from agatsuma import log

from agatsuma.interfaces import AbstractSpell, HandlingSpell
from agatsuma.framework.tornado import Url, UrlFor, AgatsumaHandler

class MTDemoSpell(AbstractSpell, HandlingSpell):
    def __init__(self):
        config = {'name' : 'Demo spell for main-thread handlers',
                  'info' : ()
                 }
        AbstractSpell.__init__(self, 'mt_demo_spell', config)
        
    def initRoutes(self, map):
        map.extend([(r"/test/mt/sync",       MTSyncHandler),
                    (r"/test/mt/async_null", MTAsyncNullHandler),
                    (r"/test/mt/async",      MTAsyncHandler),
                    Url('testurl', '/test/%(param1)s/%(param2)d',
                        MTUrlTestHandler),
                ])
    
class MTUrlTestHandler(AgatsumaHandler):
    def get(self, param1, param2):
        items = []
        items.append("param1: %s, param2: %d" % (param1, int(param2)))
        items.append("UrlFor: %s" % UrlFor('testurl',
                                         param1 = 'testparam',
                                         param2 = 10))
        self.render("template.html", items = items)

class MTSyncHandler(tornado.web.RequestHandler):
    """
    Usual sync handler
    """
    def get(self):
        self.write("Hello from MTSyncHandler")

class MTAsyncNullHandler(tornado.web.RequestHandler):
    """
    Sync handler in async notation
    """
    @tornado.web.asynchronous
    def get(self):
        self.write("Hello from MTAsyncNullHandler")
        self.finish()       
       
class MTAsyncHandler(tornado.web.RequestHandler):
    """
    Async handler. Work performed in main thread.
    """    
    @tornado.web.asynchronous
    def get(self):
        self.write("Hello from MTAsyncHandler<br/>")
        self.count = 0
        tornado.ioloop.IOLoop.instance().add_timeout( 
              time.time() + 1, 
              self.async_callback(self.async_send)) 
        
    def async_send(self):
        self.write("Iteration %d completed<br/>" % self.count)
        self.flush()
        if self.count > 3:
            self.finish()
        else:
            self.count += 1
            tornado.ioloop.IOLoop.instance().add_timeout( 
              time.time() + 1, 
              self.async_callback(self.async_send)) 
