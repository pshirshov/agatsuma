# -*- coding: utf-8 -*-

"""
.. module:: mp_core
   :synopsis: Multiprocessing core
"""

import os
import threading
import multiprocessing
from multiprocessing import Pool, Manager

from agatsuma import Settings, log
from agatsuma.errors import EAbstractFunctionCall
#from agatsuma.core import Core
from agatsuma.interfaces import PoolEventSpell
from agatsuma.interfaces import AbstractCoreExtension

"""
     Base core extension providing pool of worker processes and able to
notify them about settings changes.

.. warning:: If you want to change settings from worker threads you should call :meth:`agatsuma.core.MPCore.startSettingsUpdater` recently after core initialization.

``MPCore`` uses timer for updating settings in main process. It may be not really
good if you using Agatsuma with another library which provides periodic
callbacks. If so you should override method :meth:`agatsuma.core.MPCore.startSettingsUpdater`
in core subclass and don't spawn unwanted thread.

.. note:: The only way to shutdown multiprocessing application correctly from another application is sending of ``SIGTERM`` signal to main process.


    def startSettingsUpdater(self):
         Initiates periodic checking for config updates. May be overriden in
        subclasses
"""

class MultiprocessingCoreExtension(AbstractCoreExtension):
    def init(self, core, appDirs, appConfig, kwargs):
        spellsDirs = []
        nsFragments = ('agatsuma', 'spells', 'supplemental', 'mp')
        spellsDirs.extend ([core._internalSpellSpace(*nsFragments)
                            ])
        spellsDirs.extend(kwargs.get('spellsDirs', []))
        kwargs['spellsDirs'] = spellsDirs
        return (appDirs, appConfig, kwargs)

    def additional_methods(self):
        return [("start_settings_updater", self.startSettingsUpdater),
                ("remember_pid", self.rememberPid),
                ("write_pid", self.writePid)
                ]

    @staticmethod
    def name():
        return "multiprocessing"

    def on_core_post_configure(self, core):
        """
        spellsDirs = []
        nsFragments = ('agatsuma', 'framework', 'tornado', 'spells')
        spellsDirs.extend ([self._internalSpellSpace(*nsFragments)
                            ])
        """
        MultiprocessingCoreExtension.removePidFile()
        log.mpcore.info("Calling pre-pool-init routines...")
        #self._prePoolInit() # TODO: XXX:
        for spell in core.implementationsOf(PoolEventSpell):
            spell.prePoolInit(core)

        core.pool = None
        workers = Settings.mpcore.workers
        if workers >= 0:
            log.mpcore.debug("Starting %d workers..." % workers)
            core.pool = Pool(processes=workers,
                             initializer = _workerInitializer,
                             initargs = (Settings.mpcore.settings_update_timeout, ))
        else:
            log.mpcore.info("Pool initiation skipped due negative workers count")

        log.mpcore.info("Calling post-pool-init routines...")
        for spell in core.implementationsOf(PoolEventSpell):
            spell.postPoolInit(core)
        self.pool = core.pool

    def on_core_stop(self, core):
        if core.pool:
            core.pool.close()
        self.removePidFile()

################################################
    configUpdateManager = Manager()
    sharedConfigData = configUpdateManager.dict()
    pids = configUpdateManager.list()

    # TODO: XXX: one method enough
    @staticmethod
    def rememberPid(pid):
        assert type(pid) is int
        MultiprocessingCoreExtension.pids.append(pid)

    @staticmethod
    def writePid(pid):
        log.mpcore.debug("Writing PID %d" % pid)
        mode = "a+"
        pidfile = Settings.mpcore.pidfile
        if not os.path.exists(pidfile):
            mode = "w+"
        f = open(pidfile, mode)
        f.write("%d\n" % pid)
        f.close()

    @staticmethod
    def removePidFile():
        log.mpcore.debug("Removing pidfile...")
        pidfile = Settings.mpcore.pidfile
        if os.path.exists(pidfile):
            os.remove(pidfile)

    def startSettingsUpdater(self):
        """ Initiates periodic checking for config updates. May be overriden in
        subclasses """
        if self.pool:
            self._startSettingsUpdater()
        else:
            log.mpcore.info("Settings updater is not started in main thread due empty process' pool")

    def _startSettingsUpdater(self):
        raise EAbstractFunctionCall()

    @staticmethod
    def _updateSettings():
        # Settings in current thread are in old state
        # If we detect, that shared object has updated config we replace it
        process = multiprocessing.current_process()
        thread = threading.currentThread()
        log.mpcore.info("Checking for config updates in process '%s' with PID %s using thread '%s'..."
                          % (str(process.name), process.pid, thread.getName()))

        prevUpdate = Settings.configData['update']
        lastUpdate = MultiprocessingCoreExtension.sharedConfigData['update']
        if (prevUpdate < lastUpdate):
            process = multiprocessing.current_process()
            thread = threading.currentThread()
            log.mpcore.info("Process '%s' with PID %s received new config, updating using thread '%s'..."
                          % (str(process.name), process.pid, thread.getName()))
            #Core.settings.parseSettings(Core.sharedConfigData['data'], Settings.descriptors)
            Settings.setConfigData(MultiprocessingCoreExtension.sharedConfigData['data'], updateShared = False)

def _workerInitializer(timeout):
    process = multiprocessing.current_process()
    MultiprocessingCoreExtension.rememberPid(process.pid)
    MultiprocessingCoreExtension.writePid(process.pid)
    log.mpcore.debug("Initializing worker process '%s' with PID %d. Starting config update checker with %ds timeout" % (str(process.name), process.pid, timeout))
    MPStandaloneExtension._updateSettingsByTimer(timeout)

class MPStandaloneExtension(MultiprocessingCoreExtension):
    def _startSettingsUpdater(self):
        MultiprocessingCoreExtension._updateSettingsByTimer(Settings.mpcore.settings_update_timeout)

    @staticmethod
    def _updateSettingsByTimer(timeout):
        threading.Timer(timeout, MPStandaloneExtension._updateSettingsByTimer, (timeout, )).start()
        MultiprocessingCoreExtension._updateSettings()
