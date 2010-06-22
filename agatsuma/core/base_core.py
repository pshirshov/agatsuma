# -*- coding: utf-8 -*-
"""
.. module:: base_core
   :synopsis: Basic core
"""
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
    """Base core which provides basic services, such as settings
and also able to enumerate spells.

:param appDir: path to directory containing application spells
:param appConfig: path to JSON file with application settings

The following kwargs parameters are supported:

    #. `appName` : Application name
    #. `appSpells` : names of namespaces to search spells inside
    #. `spellsDirs` : additional (to `appDir`) directories to search spells inside

.. attribute:: instance

   The core instance. Only one core may be instantiated during application
   lifetime.

.. attribute:: versionString

   Full Agatsuma version including commit identifier and branch.
   May be extracted from GIT repository with `getversion` script.
   
    """
    instance = None
    versionString = "%d.%d.%d.%s.%s" % (majorVersion, minorVersion, commitsCount, branchId, commitId)
        
    def __init__(self, appDir, appConfig, **kwargs):
        assert Core.instance is None
        Core.instance = self
        
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

        if appConfig:
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
        else:
            log.core.critical("Config path is None")

        log.core.info("Initialization completed")
        signal.signal(signal.SIGTERM, self._sigHandler)

    def _stop(self):
        """
        Empty virtual function intended to be overriden in subclasses.
        Runs before core shutdown.
        """
        pass
    
    def _postConfigure(self):
        pass

    def _sigHandler(self, signum, frame):
        log.core.debug("Received signal %d" % signum)
        self.stop()

    def stop(self):
        """
        This method is intended to stop core. Subclasses may override method
        :meth:`agatsuma.core.Core._stop` to perform some cleanup actions here.
        """
        log.core.info("Stopping Agatsuma...")
        self._stop()

    def implementationsOf(self, InterfaceClass):
        #TODO: caching (maybe caching decorator?)
        """ The most important function for Agatsuma-based application.
        It returns all the spells implementing interface `InterfaceClass`.
        """
        return self._implementationsOf(InterfaceClass)

    def _implementationsOf(self, InterfaceClass):
        return filter(lambda spell: issubclass(type(spell), InterfaceClass), self.spells)

    def registerOption(self, settingName, settingType, settingComment):
        """ This function must be called from
:meth:`agatsuma.interfaces.AbstractSpell.preConfigure`

**TODO**

:param settingName: String contains of two *group name* and *option name* separated with dot (``group.option`` for example). Option will be threated as read-only if the string begins with exclamation mark.
:param settingType: type for option value. Allowed all types compatible with JSON.
:param settingComment: string with human-readable description for option

See also **TODO**
"""
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
        """ This method is intended to register *entry points*.
        Entry point is arbitrary function which receives
        arbitrary argumets list. Entry point may be called via
        :meth:`agatsuma.core.Core.runEntryPoint`. Core and services are fully initialized when
        entry point became available, so it may be used to perform
        different tasks that requires fully initialized environment such
        as database cleanup or something else.
        """
        if not entryPointId in self.entryPoints:
            self.entryPoints[entryPointId] = epFn
        else:
            raise Exception("Entry point with name '%s' is already registered" % entryPointId)

    def runEntryPoint(self, name, *args, **kwargs):
        """ This method runs registered entry point with given `name`
        with arguments `*args` and `**kwargs`.

        You should manually call this method from your application code when
        you need to run entry point.

        Basic Agatsuma's services provides several usable
        :ref:`entry points<std-entry-points>`.
        """
        self.entryPoints[name](*args, **kwargs)
        
