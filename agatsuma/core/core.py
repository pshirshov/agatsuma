# -*- coding: utf-8 -*-
import os
import re
import logging
import signal

from weakref import WeakValueDictionary

from agatsuma import Enumerator
from agatsuma import log
from agatsuma import Settings

majorVersion = 0
minorVersion = 1
try:
    from agatsuma.version import commitsCount, branchId, commitId
except:
    commitsCount = 0
    branchId = "branch"
    commitId = "commit"

class Core(object):
    """ Ololo
    """
    instance = None
    
    def __init__(self, appDir, appConfig, **kwargs):
        assert Core.instance is None
        Core.instance = self
        
        self.versionString = "%d.%d.%d.%s.%s" % (majorVersion, minorVersion, commitsCount, branchId, commitId)
        
        self.logger = log()
        self.logger.initiateLoggers()
        log.newLogger("core", logging.DEBUG)
        log.core.info("Initializing Agatsuma")
        log.core.info("Version: %s" % self.versionString)
        
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
        
        self._postConfigure()

        log.core.info("Initialization completed")
        signal.signal(signal.SIGTERM, self.sigHandler)

    def _stop(self):
        pass
    
    def _postConfigure(self):
        pass

    def runEntryPoint(self, name, argv):
        self.entryPoints[name](argv)

    def sigHandler(self, signum, frame):
        log.core.debug("Received signal %d" % signum)
        self.stop()
    
    def stop(self):
        log.core.info("Stopping Agatsuma...")
        if self.pool:
            self.pool.close()
        self._stop()
    
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

