# -*- coding: utf-8 -*-
"""
.. module:: base_core
   :synopsis: Basic core
"""
import os
import re
import signal

from agatsuma import Enumerator
from agatsuma import log
from agatsuma import Settings

major_version = 0
minor_version = 2
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

.. attribute:: agatsuma_base_dir

   Path to directory which contains Agatsuma. This directory makes Agatsuma's
   namespaces available when added into ``PYTHONPATH``.
    """
    instance = None
    version_string = "%d.%d.%d.%s.%s" % (major_version, minor_version, commits_count, branch_id, commit_id)
    internal_state = {"mode":"normal"}
    agatsuma_base_dir = up(up(os.path.realpath(os.path.dirname(__file__))))

    @staticmethod
    def _i_internal_spell_space(*fragments):
        basePath = os.path.join(Core.agatsuma_base_dir, *fragments)
        baseNS = '.'.join(fragments)
        return (basePath, baseNS)

    def __init__(self, app_directorys, appConfig, **kwargs):
        assert Core.instance is None
        Core.instance = self

        self.logger = log()
        self.logger.initiate_loggers()
        log.new_logger("core")
        log.new_logger("storage")
        log.core.info("Initializing Agatsuma")
        log.core.info("Version: %s" % self.version_string)
        log.core.info("Agatsuma's base directory: %s" % self.agatsuma_base_dir)

        self.shutdown = False
        
        self.extensions = []
        coreExtensions = kwargs.get("core_extensions", [])
        for extensionClass in coreExtensions:
            log.core.info("Instantiating core extension '%s'..." % extensionClass.name())
            extension = extensionClass()
            (app_directorys, appConfig, kwargs) = extension.init(self, app_directorys, appConfig, kwargs)
            methods = extension.additional_methods()
            for method_name, method in methods:
                setattr(self, method_name, method)
                log.core.debug("Extension method '%s' added to core's interface" % method_name)
            self.extensions.append(extension)

        self.app_name = kwargs.get("app_name", None)
        self.application_spells = kwargs.get("application_spells", [])
        self.spell_directories = kwargs.get("spell_directories", [])
        Core.internal_state["mode"] = kwargs.get("app_mode", "normal")

        self.spells = []
        self.spellbook = {}
        self.registered_settings = {}
        self.entry_points = {}

        #self.global_filters_list = [] #TODO: templating and this
        forbidden_spells = kwargs.get("forbidden_spells", [])
        enumerator = Enumerator(self, app_directorys, forbidden_spells)

        self.spell_directories.append(self._i_internal_spell_space('agatsuma', 'spells', 'common'))
        enumerator.enumerate_spells(self.application_spells, self.spell_directories)

        if appConfig:
            from agatsuma.interfaces.abstract_spell import AbstractSpell
            log.core.info("Initializing spells...")
            for spell in self.implementations_of(AbstractSpell):
                spell.pre_configure(self)
            self.settings = Settings(appConfig, self.registered_settings)
            self.logger.update_levels()
            log.core.info("Calling post-configure routines...")
            for spell in self.implementations_of(AbstractSpell):
                spell.post_configure(self)
            log.core.info("Spells initialization completed")
            self._post_configure()
            enumerator.eagerUnload()
        else:
            log.core.critical("Config path is None")

        log.core.info("Initialization completed")
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _stop(self):
        """
        Empty virtual function intended to be overriden in subclasses.
        Runs before core shutdown.
        """
        for extension in self.extensions:
            extension.on_core_stop(self)

    def _post_configure(self):
        for extension in self.extensions:
            extension.on_core_post_configure(self)

    def _signal_handler(self, signum, frame):
        log.core.debug("Received signal %d" % signum)
        self.stop()

    def stop(self):
        """
        This method is intended to stop core. Subclasses may override method
        :meth:`agatsuma.core.Core._stop` to perform some cleanup actions here.
        """
        log.core.info("Stopping Agatsuma...")
        self.shutdown = True
        self._stop()

    def implementations_of(self, InterfaceClass):
        """ The most important function for Agatsuma-based application.
        It returns all the spells implementing interface `InterfaceClass`.
        """
        return filter(lambda spell: issubclass(type(spell), InterfaceClass), self.spells)

    def register_option(self, settingName, settingType, settingComment):
        """ This function must be called from
:meth:`agatsuma.interfaces.AbstractSpell.pre_configure`

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
            if fqn in self.registered_settings:
                raise Exception("Setting is already registered: '%s' (%s)" % (fqn, settingComment))
            self.registered_settings[fqn] = settingDescr
        else:
            raise Exception("Bad setting name: '%s' (%s)" % (settingName, settingComment))

    def register_entry_point(self, entry_pointId, epFn):
        """ This method is intended to register *entry points*.
        Entry point is arbitrary function which receives
        arbitrary argumets list. Entry point may be called via
        :meth:`agatsuma.core.Core.run_entry_point`. Core and services are fully initialized when
        entry point became available, so it may be used to perform
        different tasks that requires fully initialized environment such
        as database cleanup or something else.
        """
        if not entry_pointId in self.entry_points:
            self.entry_points[entry_pointId] = epFn
        else:
            raise Exception("Entry point with name '%s' is already registered" % entry_pointId)

    def run_entry_point(self, name, *args, **kwargs):
        """ This method runs registered entry point with given `name`
        with arguments `*args` and `**kwargs`.

        You should manually call this method from your application code when
        you need to run entry point.

        Basic Agatsuma's services provides several usable
        :ref:`entry points<std-entry-points>`.
        """
        self.entry_points[name](*args, **kwargs)
