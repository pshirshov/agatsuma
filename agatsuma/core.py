# -*- coding: utf-8 -*-
import os
import re
import logging
import signal

import threading
import multiprocessing
from multiprocessing import Pool, Manager
from weakref import WeakValueDictionary

from agatsuma.enumerator import Enumerator
from agatsuma.log import log
from agatsuma.settings import Settings

"""
Warning: common core is only able to propagate settings update to process 
         pool. 
         Updating settings in main thread is subclass' problem
"""

def updateSettings():
    # Settings in current thread is in old state
    # If we detect, that shared object has updated config we replace it
    prevUpdate = Settings.configData['update']
    lastUpdate = Core.sharedConfigData['update']
    if (prevUpdate < lastUpdate):
        process = multiprocessing.current_process()
        log.core.info("Process '%s' with PID %s received new config, updating..." % (str(process.name), process.pid))
        #Core.settings.parseSettings(Core.sharedConfigData['data'], Settings.descriptors)
        Settings.setConfigData(Core.sharedConfigData['data'], False)

def updateSettingsByTimer(timeout):
    threading.Timer(timeout, updateSettingsByTimer, (timeout, )).start()    
    updateSettings()
    
def workerInitializer(timeout):
    process = multiprocessing.current_process()
    Core.instance.writePid(process.pid)
    Core.pids.append(process.pid)    
    log.core.debug("Initializing worker process '%s' with PID %d. Starting config update checker with %ds timeout" % (str(process.name), process.pid, timeout))
    updateSettingsByTimer(timeout)

class Core(object):
    configUpdateManager = Manager()
    sharedConfigData = configUpdateManager.dict()
    pids = configUpdateManager.list()
    instance = None
    
    def __init__(self, appDir, appConfig, **kwargs):
        assert Core.instance is None
        Core.instance = self
       
        self.logger = log()
        self.logger.initiateLoggers()
        log.newLogger("core", logging.DEBUG)
        log.core.info("Initializing Agatsuma")
        
        self.URIMap = []
        self.appName = kwargs.get("appName", None)
        self.appSpells = []
        self.appSpells.extend(kwargs.get("appSpells", [])) #"core_spells", "core_filters"])
        self.spellsDirs = []
        self.spellsDirs.extend(kwargs.get("spellsDirs", []))
        self.spells = []
        self.spellsDict = {}
        self.filterStack = []
        self.registeredSettings = {}
        self.entryPoints = {}
        
        #self.globalFilterStack = [] #TODO: templating and this
        self.mpHandlerInstances = WeakValueDictionary()
        prohibitedSpells = kwargs.get("prohibitedSpells", [])
        enumerator = Enumerator(self, appDir, prohibitedSpells)
        
        #essentialSpellSpaces = self.appSpells
        #essentialSpellSpaces = map(lambda s: "agatsuma.spells.%s" % s, essentialSpellSpaces)
        
        #libRoot = os.path.realpath(os.path.dirname(__file__))
        self.spellsDirs.extend ([os.path.join('agatsuma', 'spells')]) #[os.path.join(libRoot, 'spells')])
        enumerator.enumerateSpells(self.appSpells, self.spellsDirs)

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
        
        self.removePid()
        self._prePoolInit()
        
        workers = Settings.core.workers
        log.core.debug("Starting %d workers..." % workers)
        self.pool = Pool(processes=workers, 
                         initializer = workerInitializer, 
                         initargs = (Settings.core.settings_update_timeout, ))
        
        log.core.info("Calling post-pool-init routines...")
        for spell in self._implementationsOf(AbstractSpell):
            spell.postPoolInit(self)

        log.core.info("Initialization completed")
        signal.signal(signal.SIGTERM, self.sigHandler)

    def _prePoolInit(self):
        pass
    
    def _stop(self):
        pass

    def writePid(self, pid):
        mode = "a+"
        pidfile = Settings.core.pidfile
        if not os.path.exists(pidfile):
            mode = "w+"            
        f = open(pidfile, mode)
        f.write("%d\n" % pid)
        f.close()
        
    def removePid(self):
        pidfile = Settings.core.pidfile
        if os.path.exists(pidfile):
            os.remove(pidfile)

    def runEntryPoint(self, name, argv):
        self.entryPoints[name](argv)

    def sigHandler(self, signum, frame):
        log.core.debug("Received signal %d" % signum)
        self.stop()
    
    def stop(self):
        log.core.info("Stopping Agatsuma...")
        self.pool.close()
        self._stop()
        self.removePid()
    
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
        
    def registerEntryPoint(self, entryPointId, epFn):
        if not entryPointId in self.entryPoints:
            self.entryPoints[entryPointId] = epFn
        else:
            raise Exception("Entry point with name '%s' is already registered" % entryPointId)

