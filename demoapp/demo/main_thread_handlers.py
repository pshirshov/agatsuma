# -*- coding: utf-8 -*-

import tornado.web
import tornado.ioloop
import time
from agatsuma.core import Core
from agatsuma.settings import Settings
from agatsuma.log import log

from agatsuma.interfaces.abstract_spell import AbstractSpell
from agatsuma.interfaces.handling_spell import HandlingSpell

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
                ])
    

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
