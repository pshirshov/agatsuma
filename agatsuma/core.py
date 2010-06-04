# -*- coding: utf-8 -*-
import logging
import signal
import Queue

import tornado.httpserver
import tornado.ioloop
import tornado.web

from multiprocessing import Pool
from multiprocessing import Queue as MPQueue

from agatsuma.enumerator import Enumerator
from agatsuma.log import log
from agatsuma.settings import Settings
#from agatsuma.spells import core as CoreSpell

import tornado.autoreload
from weakref import WeakValueDictionary

import re
#import time
#import pickle

"""
import copy_reg
import types

def reduce_method(m):
    return (getattr, (m.__self__, m.__func__.__name__))

copy_reg.pickle(types.MethodType, reduce_method)
"""

import multiprocessing
import threading
from multiprocessing import Manager

#manager = Manager()
#sharedConfigContent = manager.Value('u', "")
#sharedConfig = manager

def updateSettings(timeout):
    threading.Timer(timeout, updateSettings, (timeout, )).start()    
    # Settings in current thread is in old state
    # If we detect, that shared object has updated config
    # we reparse it
    prevUpdate = Settings.configData['update']
    lastUpdate = Core.sharedConfigData['update']
    if (prevUpdate < lastUpdate):
        log.core.info("Thread %s received new config, updating..." % str( multiprocessing.current_process()))
        #Core.settings.parseSettings(Core.sharedConfigData['data'], Settings.descriptors)
        Settings.setConfigData(Core.sharedConfigData['data'], False)

def workerInitializer(timeout):
    pid = multiprocessing.current_process().pid
    Core.instance.writePid(pid)
    Core.pids.append(pid)    
    log.core.debug("Initializing thread %s. Starting config update checker with %ds timeout" % (multiprocessing.current_process(), timeout))
    updateSettings(timeout)

class Core(tornado.web.Application):
    mqueue = None
    configUpdateManager = Manager()
    sharedConfigData = configUpdateManager.dict()
    pids = configUpdateManager.list()
    instance = None

    def writePid(self, pid, recreate = False):
        mode = "a+"
        if recreate:
            mode = "w+"
        f = open(Settings.core.pidfile, mode)
        f.write("%d\n" % pid)
        f.close()
        
    def __init__(self, appDir, appConfig, **kwargs):
        assert Core.instance is None
        Core.instance = self
        tornado.autoreload.start()
        self.ioloop = tornado.ioloop.IOLoop.instance()
        
        self.logger = log()
        self.logger.initiateLoggers()
        log.newLogger("core", logging.DEBUG)
        log.core.info("Initializing Agatsuma")
        
        self.URIMap = []
        self.appName = kwargs.get("appName", None)
        self.appSpells = kwargs.get("appSpells", ["core_spells", "core_filters"])
        self.spells = []
        self.spellsDict = {}
        self.filterStack = []
        self.registeredSettings = {}
        
        #self.globalFilterStack = [] #TODO: templating and this
        self.mpHandlerInstances = WeakValueDictionary()
        enumerator = Enumerator(self, appDir)
        essentialSpellSpaces = self.appSpells
        essentialSpellSpaces = map(lambda s: "agatsuma.spells.%s" % s, essentialSpellSpaces)
        enumerator.enumerateSpells(essentialSpellSpaces)
        #print self.registeredSettings

        from agatsuma.interfaces.abstract_spell import AbstractSpell
        log.core.info("Initializing spells...")
        for spell in self._implementationsOf(AbstractSpell):
            spell.preConfigure(self)
        self.settings = Settings(appConfig, self.registeredSettings)
        self.logger.updateLevels()
        log.core.info("Calling post-configure routines...")
        for spell in self._implementationsOf(AbstractSpell):
            spell.postConfigure(self)
        log.core.info("Spells initialization completed")    

        pid = multiprocessing.current_process().pid
        Core.pids.append(pid)
        self.writePid(pid, True)
        
        self.messagePumpNeeded = False
        from agatsuma.handler import MsgPumpHandler
        for uri, handler in self.URIMap:
            if issubclass(handler, MsgPumpHandler):
                self.messagePumpNeeded = True
                Core.mqueue = MPQueue()
                self.waitingCallbacks = []
                break       
                
        workers = Settings.core.workers
        log.core.debug("Main process' PID: %d" % pid)
        log.core.debug("Starting %d workers..." % workers)
        self.pool = Pool(processes=workers, initializer = workerInitializer, initargs = (Settings.core.settings_update_timeout, ))
        
        log.core.info("Calling post-pool-init routines...")
        for spell in self._implementationsOf(AbstractSpell):
            spell.postPoolInit(self)
        
        tornado.web.Application.__init__(self, self.URIMap)
        log.core.info("Initialization completed")
        signal.signal(signal.SIGTERM, self.sigHandler)
    
    def start(self):
        #self.application = (self.URIMap)
        port = Settings.core.port
        pumpTimeout = Settings.core.message_pump_timeout
        assert len(self.URIMap) > 0

        self.logger.setMPHandler(self.ioloop)
        self.HTTPServer = tornado.httpserver.HTTPServer(self)
        self.HTTPServer.listen(port)
        if self.messagePumpNeeded:
            mpump = tornado.ioloop.PeriodicCallback(self.messagePump , pumpTimeout, io_loop=self.ioloop)
            log.core.debug("Starting message pump...")
            mpump.start()
        else:
            log.core.debug("Message pump initiation skipped, it isn't required for any spell")
        log.core.info("=" * 60)
        log.core.info("Starting %s/Agatsuma in server mode on port %d..." % (self.appName, port))
        log.core.info("=" * 60)
        self.ioloop.start()

    def sigHandler(self, signum, frame):
        log.core.debug("Received signal %d" % signum)
        self.stop()
        
    def stop(self):
        log.core.info("Stopping Agatsuma...")
        self.pool.close()
        #self.HTTPServer.stop()
        self.ioloop.stop()
        
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
        
    def _implementationsOf(self, InterfaceClass):
        return filter(lambda spell: issubclass(type(spell), InterfaceClass), self.spells)

    def registerOption(self, settingName, settingType, settingComment):
        if not getattr(self, "settingRe", None):
            self.settingRe = re.compile(r"^(!{0,1})((\w+)\.{0,1}(\w+))$")
        match = self.settingRe.match(settingName)
        if match:
            settingDescr = (match.group(3), 
                            match.group(4),
                            bool(match.group(1)), 
                            settingType,
                            settingComment,
                           )
            fqn = match.group(2)
            if fqn in self.registeredSettings:
                raise Exception("Setting is already registered: '%s' (%s)" % (fqn, settingComment))
            self.registeredSettings[fqn] = settingDescr
        else:
            raise Exception("Bad setting name: '%s' (%s)" % (settingName, settingComment))
