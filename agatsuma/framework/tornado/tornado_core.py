# -*- coding: utf-8 -*-
import multiprocessing
from multiprocessing import Queue as MPQueue

import tornado.httpserver
import tornado.ioloop
import tornado.web

from agatsuma.core import Core, updateSettings
from agatsuma.settings import Settings
from agatsuma.log import log

class TornadoCore(Core, tornado.web.Application):   
    mqueue = None
   
    def __init__(self, appDir, appConfig, **kwargs):
        Core.__init__(self, appDir, appConfig, **kwargs)
        tornado.web.Application.__init__(self, self.URIMap, 
                                         debug = Settings.core.debug, # autoreload
                                        )
    def _prePoolInit(self):
        self.messagePumpNeeded = False
        from agatsuma.framework.tornado import MsgPumpHandler
        for uri, handler in self.URIMap:
            if issubclass(handler, MsgPumpHandler):
                self.messagePumpNeeded = True
                TornadoCore.mqueue = MPQueue()
                self.waitingCallbacks = []
                break      

    def _stop(self):
        #self.HTTPServer.stop()
        self.ioloop.stop()

    def start(self):
        self.ioloop = tornado.ioloop.IOLoop.instance()
        port = Settings.core.port
        pumpTimeout = Settings.core.message_pump_timeout
        assert len(self.URIMap) > 0

        self.logger.setMPHandler(self.ioloop)
        self.HTTPServer = tornado.httpserver.HTTPServer(self)
        self.HTTPServer.listen(port)
        """
        # Preforking is only available in Tornado GIT
        if Settings.core.forks > 0:
            self.HTTPServer.bind(port)
            self.HTTPServer.start()
        """
        pid = multiprocessing.current_process().pid
        Core.pids.append(pid)
        self.writePid(pid)
        log.core.debug("Main process' PID: %d" % pid)
        configChecker = tornado.ioloop.PeriodicCallback(updateSettings, 
                                                        1000 * Settings.core.settings_update_timeout, 
                                                        io_loop=self.ioloop)        
        configChecker.start()
        
        if self.messagePumpNeeded:
            mpump = tornado.ioloop.PeriodicCallback(self.messagePump, 
                                                    pumpTimeout, 
                                                    io_loop=self.ioloop)
            log.core.debug("Starting message pump...")
            mpump.start()
        else:
            log.core.debug("Message pump initiation skipped, it isn't required for any spell")
        log.core.info("=" * 60)
        log.core.info("Starting %s/Agatsuma in server mode on port %d..." % (self.appName, port))
        log.core.info("=" * 60)
        self.ioloop.start()
        
    def messagePump(self):
        while not self.mqueue.empty():
            try:
                message = self.mqueue.get_nowait()
                if Settings.core.debug_level > 0:
                    log.core.debug("message: '%s'" % str(message))
                if message and type(message) is tuple:
                    handlerId = message[0]
                    if handlerId in self.mpHandlerInstances:
                        self.mpHandlerInstances[handlerId].processMessage(message)
                    else:
                        log.core.warning("unknown message recepient: '%s'" % str(message))
                else:
                    log.core.debug("bad message: '%s'" % str(message))
            except Queue.Empty, e:
                log.core.debug("message: raised Queue.Empty")
                    
        if self.waitingCallbacks:
            try:
                for callback in self.waitingCallbacks:
                    callback()
            finally:
                self.waitingCallbacks = []
            
    def handlerInitiated(self, handler):
        # references are weak, so handler will be correctly destroyed and removed from dict automatically
        self.mpHandlerInstances[id(handler)] = handler        
