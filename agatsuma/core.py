# -*- coding: utf-8 -*-
"""
.. module:: base_core
   :synopsis: Basic core
"""
import logging
import os
import re
import signal

from agatsuma import LoggingSystem
#from agatsuma import Spellbook

major_version = 0
minor_version = 3
try:
    from agatsuma.version import commits_count, branch_id, commit_id
except Exception, e:
    print "Cannot obtain version information: %s" % str(e)
    commits_count = 0
    branch_id = "branch"
    commit_id = "commit"

def up(p):
    return os.path.split(p)[0]

class Core(object):
    """Base core which provides basic services, such as settings
and also able to enumerate spells.

:param app_directorys: list of paths to directories containing application spells.

.. note:: All the paths in ``app_directorys`` list must define importable namespaces. So if we replace all '/' with '.'  in such path we should get importable namespace

.. note:: app_directorys also may contain tuples with two values (``dir``, ``ns``) where ``ns`` is namespace corresponding to directory ``dir`` but it's not recommended to use this feature.

:param appConfig: path to JSON file with application settings

The following kwargs parameters are supported:

    #. `app_name` : Application name
    #. `application_spells` : names of namespaces to search spells inside
    #. `spell_directories` : additional (to `app_directory`) directories to search spells inside

.. attribute:: instance

   The core instance. Only one core may be instantiated during application
   lifetime.

.. attribute:: version_string

   Full Agatsuma version including commit identifier and branch.
   May be extracted from GIT repository with `getversion` script.

.. attribute:: internal_state

   Dict. For now contains only the key ``mode`` with value ``setup`` when core
   was started from setup.py and ``normal`` otherwise.

    """
    version_string = "%d.%d.%d.%s.%s" % (major_version, minor_version, commits_count, branch_id, commit_id)
    internal_state = {"mode":"normal"}

    instance = None
    
    def __new__(cls, *a, **kva):
        '''
        Singleton getter/creator
        @return: Agatsuma Core
        '''
        if cls.instance is None:
            cls.instance = object.__new__(cls, *a, **kva)
        return cls.instance
    
    def __init__(self, app_name, app_config_path, **kwargs):
        self.logger = LoggingSystem()
        self.logger.core.info("Initializing Agatsuma v%s" % self.version_string)
        
        #update internal state
        Core.internal_state["mode"] = kwargs.get("app_mode", "normal")
        
        #set up application name
        self.app_name = kwargs.get("app_name", None)
        
        #ok, we have all what we need and we can setup low level core extensions
        self.setup_core_extensions(kwargs.get("core_extensions", []))

        #i dont know what is it
        #self.registered_settings = {}
        #self.entry_points = {}
        

        #need to check config before working
        if not app_config_path or len(app_config_path) < 7:
            self.logger.core.critical("Config path is None or length of path lower than 7 symbols!")
            #perhaps, we dont need to create mode w/o config
            #return
        
        
        #if config is ok 
        else:
            self.logger.core.info("Loading settings manager")
            #parse config and load settings
            #self.settings = SettingsManager(app_config_path)
            
#            from agatsuma.interfaces.abstract_spell import AbstractSpell
#            log.core.info("Initializing spells...")
#            allTheSpells = self.spellbook.implementations_of(AbstractSpell)
#            for spell in allTheSpells:
#                spell.pre_configure(self)
#            self.settings = Settings(appConfig, self.registered_settings)
#            self.logger.update_levels()
#            log.core.info("Calling post-configure routines...")
#            for spell in allTheSpells:
#                spell.post_configure(self)
#            log.core.info("Spells initialization completed")
#            self._post_configure()
#            enumerator.eagerUnload()

        
        #so, we can load spells
        self.logger.core.info("Loading SpellBook")
        #self.spellbook = Spellbook(self.app_name)
        
        #alert all extensions, we're ready to play
        self.logger.core.debug("Post config extensions executing") 
        for extension in self.extensions:
            self.logger.core.debug("Executing of '%s'" % (extension.name()))
            extension.on_core_post_configure(self)
        self.logger.core.debug("Post config extensions executing completed")   

        
        self.logger.core.info("Initialization completed")
        signal.signal(signal.SIGTERM, self._signal_handler)

    def setup_core_extensions(self, extensions, **kwargs):
        '''
        Setup low layer core extensions
        @param extensions: list of extension instances
        '''
        self.extensions = []
        for extension_class in extensions:
            raise Exception("Not implemented yet") 
#            self.logger("core").info("Instantiating core extension '%s'..." % extension_class.name())
#            extension = extension_class()
#            (app_directorys, appConfig, kwargs) = extension.init(self, None, None, kwargs)
#            methods = extension.additional_methods()
#            for method_name, method in methods:
#                setattr(self, method_name, method)
#                log.core.debug("Extension method '%s' added to core's interface" % method_name)
#            self.extensions.append(extension)
        

    def _signal_handler(self, signum, frame):
        self.logger.core.debug("Received signal %d, stopping..." % signum)
        self.stop()

    def stop(self):
        """
        This method is intended to stop core. Subclasses may override method
        :meth:`agatsuma.core.Core._stop` to perform some cleanup actions here.
        """
        self.logger.core.info("Stopping Agatsuma...")
        for extension in self.extensions:
            extension.on_core_stop(self)
        self._stop()

#    def register_option(self, settingName, settingType, settingComment):
#        """ This function must be called from
#:meth:`agatsuma.interfaces.AbstractSpell.pre_configure`
#
#**TODO**
#
#:param settingName: String contains of two *group name* and *option name* separated with dot (``group.option`` for example). Option will be threated as read-only if the string begins with exclamation mark.
#:param settingType: type for option value. Allowed all types compatible with JSON.
#:param settingComment: string with human-readable description for option
#
#See also **TODO**
#"""
#        if not getattr(self, "settingRe", None):
#            self.settingRe = re.compile(r"^(!{0,1})((\w+)\.{0,1}(\w+))$")
#        match = self.settingRe.match(settingName)
#        if match:
#            settingDescr = (match.group(3),
#                            match.group(4),
#                            bool(match.group(1)),
#                            settingType,
#                            settingComment,
#                           )
#            fqn = match.group(2)
#            if fqn in self.registered_settings:
#                raise Exception("Setting is already registered: '%s' (%s)" % (fqn, settingComment))
#            self.registered_settings[fqn] = settingDescr
#        else:
#            raise Exception("Bad setting name: '%s' (%s)" % (settingName, settingComment))
#
#    def register_entry_point(self, entry_pointId, epFn):
#        """ This method is intended to register *entry points*.
#        Entry point is arbitrary function which receives
#        arbitrary argumets list. Entry point may be called via
#        :meth:`agatsuma.core.Core.run_entry_point`. Core and services are fully initialized when
#        entry point became available, so it may be used to perform
#        different tasks that requires fully initialized environment such
#        as database cleanup or something else.
#        """
#        if not entry_pointId in self.entry_points:
#            self.entry_points[entry_pointId] = epFn
#        else:
#            raise Exception("Entry point with name '%s' is already registered" % entry_pointId)
#
#    def run_entry_point(self, name, *args, **kwargs):
#        """ This method runs registered entry point with given `name`
#        with arguments `*args` and `**kwargs`.
#
#        You should manually call this method from your application code when
#        you need to run entry point.
#
#        Basic Agatsuma's services provides several usable
#        :ref:`entry points<std-entry-points>`.
#        """
#        self.entry_points[name](*args, **kwargs)