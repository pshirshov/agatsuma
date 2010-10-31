# -*- coding: utf-8 -*-
import Queue
import multiprocessing
from multiprocessing import Queue as MPQueue
from weakref import WeakValueDictionary

from agatsuma.core import Core
from agatsuma.core import MultiprocessingCoreExtension
if Core.internal_state.get("mode", None) == "normal":
    import tornado.httpserver
    import tornado.ioloop
    import tornado.web
    import tornado.wsgi
    import tornado
    TornadoAppClass = tornado.web.Application
    TornadoWSGIClass = tornado.wsgi.WSGIContainer
    TornadoVersion = tornado.version
else:
    TornadoAppClass = object
    TornadoWSGIClass = object
    TornadoVersion = None

from agatsuma import Settings
from agatsuma.errors import EAbstractFunctionCall
from agatsuma import log, MPLogHandler

class TornadoMPExtension(MultiprocessingCoreExtension):
    @staticmethod
    def name():
        return "tornadomp"

    def _start_settings_updater(self):
        configChecker = tornado.ioloop.PeriodicCallback(MultiprocessingCoreExtension._update_settings,
                                                        1000 * Settings.mpcore.settings_update_timeout,
                                                        io_loop=Core.instance.ioloop)
        configChecker.start()

supported_tornado_version="0.2"

class TornadoCore(Core):
    mqueue = None
    
    def __init__(self, app_directory, appConfig, **kwargs):
        spell_directories = []
        nsFragments = ('agatsuma', 'web', 'tornado', 'spells', 'common')
        spell_directories.extend ([self._internal_spell_space(*nsFragments)
                            ])
        spell_directories.extend(kwargs.get('spell_directories', []))
        kwargs['spell_directories'] = spell_directories
        extensions = kwargs.get('core_extensions', [])
        extensions.append(TornadoMPExtension)
        kwargs['core_extensions'] = extensions
        Core.__init__(self, app_directory, appConfig, **kwargs)
        if TornadoVersion and supported_tornado_version < TornadoVersion:
            log.tcore.info("Current Tornado version: %s" %(TornadoVersion, ))
            log.tcore.warning("Current Tornado version is not supported: %s>%s" % (TornadoVersion, supported_tornado_version))

    def _stop(self):
        #self.HTTPServer.stop()
        self.ioloop.stop()
        Core._stop(self)

    def processLog(self):
        while not log.instance.logQueue.empty():
            try:
                message = log.instance.logQueue.get_nowait()
                log.rootHandler.realHandler.emit(message)
            except Queue.Empty:
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
        self.__updateLogger()
        port = Settings.tornado.port

        #self.logger.setMPHandler(self.ioloop)
        self.HTTPServer = tornado.httpserver.HTTPServer(self,
                                                        xheaders=Settings.tornado.xheaders,
                                                        # For future Tornado versions
                                                        #ssl_options=Settings.tornado.ssl_parameters
                                                       )
        """
        # Preforking is only available in Tornado GIT
        if Settings.core.forks > 0:
            self.HTTPServer.bind(port)
            self.HTTPServer.start()
        else:
        """
        self.HTTPServer.listen(port)
        pid = multiprocessing.current_process().pid

        self.remember_pid(pid)
        self.write_pid(pid)

        log.tcore.debug("Main process' PID: %d" % pid)

        self.start_settings_updater()

        self._before_ioloop_start()

        log.tcore.info("=" * 60)
        log.tcore.info("Starting %s/Agatsuma in server mode on port %d..." % (self.app_name, port))
        log.tcore.info("=" * 60)
        self.ioloop.start()

    def _before_ioloop_start(self):
        raise EAbstractFunctionCall()

class TornadoStandaloneCore(TornadoCore, TornadoAppClass):
    """Implements standalone Tornado server, useful to develop
    lightweight asynchronous web applications
    """
    
    def __init__(self, app_directory, appConfig, **kwargs):
        """
        """
        spell_directories = []
        nsFragments = ('agatsuma', 'web', 'tornado', 'spells', 'standalone')
        spell_directories.extend ([self._internal_spell_space(*nsFragments)
                            ])
        spell_directories.extend(kwargs.get('spell_directories', []))
        kwargs['spell_directories'] = spell_directories

        self.URIMap = []
        TornadoCore.__init__(self, app_directory, appConfig, **kwargs)
        self.mpHandlerInstances = WeakValueDictionary()
        tornadoSettings = {'debug': Settings.core.debug, # autoreload
                           'cookie_secret' : str(Settings.tornado.cookie_secret),
                          }
        tornadoSettings.update(Settings.tornado.app_parameters)
        assert len(self.URIMap) > 0
        tornado.web.Application.__init__(self, self.URIMap, **tornadoSettings)

    def _before_ioloop_start(self):
        if self.messagePumpNeeded and self.pool:
            TornadoCore.mqueue = MPQueue()
            pumpTimeout = Settings.tornado.message_pump_timeout
            mpump = tornado.ioloop.PeriodicCallback(self._messagePump,
                                                    pumpTimeout,
                                                    io_loop=self.ioloop)
            log.tcore.debug("Starting message pump...")
            mpump.start()
        else:
            log.tcore.debug("Message pump initiation skipped, it isn't required for any spell")

    def _messagePump(self):
        """Extracts messages from message queue if any and pass them to
        appropriate controller
        """
        while not self.mqueue.empty():
            try:
                message = self.mqueue.get_nowait()
                if Settings.core.debug_level > 0:
                    log.tcore.debug("message: '%s'" % str(message))
                if message and type(message) is tuple:
                    handlerId = message[0]
                    if handlerId in self.mpHandlerInstances:
                        self.mpHandlerInstances[handlerId].process_message(message)
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

class TornadoWSGICore(TornadoCore, TornadoWSGIClass):
    """Implements Tornado WSGI server, useful to run usual WSGI
    applications on top of Tornado.
    """

    def __init__(self, app_directory, appConfig, **kwargs):
        """
        """
        TornadoCore.__init__(self, app_directory, appConfig, **kwargs)

    def set_wsgi(self, wsgiapp):
        tornado.wsgi.WSGIContainer.__init__(self, wsgiapp)

    def _before_ioloop_start(self):
        pass
