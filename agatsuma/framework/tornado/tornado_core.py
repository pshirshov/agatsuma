# -*- coding: utf-8 -*-
import os
import Queue
import multiprocessing
from multiprocessing import Queue as MPQueue

from agatsuma.core import MPCore
if MPCore.internalState.get("mode", None) == "normal":
    import tornado.httpserver
    import tornado.ioloop
    import tornado.web
    TornadoAppClass = tornado.web.Application
else:
    TornadoAppClass = object

from agatsuma import Settings
from agatsuma import log, MPLogHandler

class TornadoCore(MPCore, TornadoAppClass):
    mqueue = None

    def __init__(self, appDir, appConfig, **kwargs):
        spellsDirs = []
        nsFragments = ('agatsuma', 'framework', 'tornado', 'spells')
        spellsDirs.extend ([self._internalSpellSpace(*nsFragments)
                            ])
        spellsDirs.extend(kwargs.get('spellsDirs', []))
        kwargs['spellsDirs'] = spellsDirs
        self.URIMap = []
        MPCore.__init__(self, appDir, appConfig, **kwargs)
        tornadoSettings = {'debug': Settings.core.debug, # autoreload
                           'cookie_secret' : str(Settings.tornado.cookie_secret),
                          }
        tornadoSettings.update(Settings.tornado.app_parameters)
        tornado.web.Application.__init__(self, self.URIMap, **tornadoSettings)

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
        MPCore._stop(self)

    def processLog(self):
        while not log.instance.logQueue.empty():
            try:
                message = log.instance.logQueue.get_nowait()
                log.rootHandler.realHandler.emit(message)
            except Queue.Empty, e:
                log.instance.rootHandler.realHandler.emit("log: raised Queue.Empty")

    def __updateLogger(self):
        #from agatsuma.settings import Settings
        pumpTimeout = Settings.tornado.logger_pump_timeout
        self.logger.logQueue = MPQueue()
        log.instance = self.logger
        self.logger.logPump = tornado.ioloop.PeriodicCallback(self.processLog,
                                                              pumpTimeout,
                                                              io_loop=self.ioloop)
        log.rootHandler = MPLogHandler(self.logger.logQueue, log.rootHandler)
        self.logger.logPump.start()

    def start(self):
        self.ioloop = tornado.ioloop.IOLoop.instance()
        pumpTimeout = Settings.tornado.message_pump_timeout
        port = Settings.tornado.port
        assert len(self.URIMap) > 0

        #self.logger.setMPHandler(self.ioloop)
        self.__updateLogger()
        self.HTTPServer = tornado.httpserver.HTTPServer(self,
                                                        xheaders=Settings.tornado.xheaders,
                                                        # For future Tornado versions
                                                        #ssl_options=Settings.tornado.ssl_parameters
                                                       )
        self.HTTPServer.listen(port)
        """
        # Preforking is only available in Tornado GIT
        if Settings.core.forks > 0:
            self.HTTPServer.bind(port)
            self.HTTPServer.start()
        """
        pid = multiprocessing.current_process().pid
        MPCore.rememberPid(pid)
        MPCore.writePid(pid)
        log.tcore.debug("Main process' PID: %d" % pid)

        self.startSettinsUpdater()

        if self.messagePumpNeeded:
            mpump = tornado.ioloop.PeriodicCallback(self.messagePump,
                                                    pumpTimeout,
                                                    io_loop=self.ioloop)
            log.tcore.debug("Starting message pump...")
            mpump.start()
        else:
            log.tcore.debug("Message pump initiation skipped, it isn't required for any spell")
        log.tcore.info("=" * 60)
        log.tcore.info("Starting %s/Agatsuma in server mode on port %d..." % (self.appName, port))
        log.tcore.info("=" * 60)
        self.ioloop.start()

    def startSettinsUpdater(self):
        configChecker = tornado.ioloop.PeriodicCallback(MPCore._updateSettings,
                                                        1000 * Settings.mpcore.settings_update_timeout,
                                                        io_loop=self.ioloop)
        configChecker.start()

    def messagePump(self):
        while not self.mqueue.empty():
            try:
                message = self.mqueue.get_nowait()
                if Settings.core.debug_level > 0:
                    log.tcore.debug("message: '%s'" % str(message))
                if message and type(message) is tuple:
                    handlerId = message[0]
                    if handlerId in self.mpHandlerInstances:
                        self.mpHandlerInstances[handlerId].processMessage(message)
                    else:
                        log.tcore.warning("unknown message recepient: '%s'" % str(message))
                else:
                    log.tcore.debug("bad message: '%s'" % str(message))
            except Queue.Empty:
                log.tcore.debug("message: raised Queue.Empty")

        if self.waitingCallbacks:
            try:
                for callback in self.waitingCallbacks:
                    callback()
            finally:
                self.waitingCallbacks = []

    def handlerInitiated(self, handler):
        # references are weak, so handler will be correctly destroyed and removed from dict automatically
        self.mpHandlerInstances[id(handler)] = handler
