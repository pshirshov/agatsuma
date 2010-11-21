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
from agatsuma.core import Core
from agatsuma.interfaces import IPoolEventSpell
from agatsuma.interfaces import AbstractCoreExtension

"""
     Base core extension providing pool of worker processes and able to
notify them about settings changes.

.. warning:: If you want to change settings from worker threads you should call :meth:`agatsuma.core.MPCore.start_settings_updater` recently after core initialization.

``MPCore`` uses timer for updating settings in main process. It may be not really
good if you using Agatsuma with another library which provides periodic
callbacks. If so you should override method :meth:`agatsuma.core.MPCore.start_settings_updater`
in core subclass and don't spawn unwanted thread.

.. note:: The only way to shutdown multiprocessing application correctly from another application is sending of ``SIGTERM`` signal to main process.


    def start_settings_updater(self):
         Initiates periodic checking for config updates. May be overriden in
        subclasses
"""

class MultiprocessingCoreExtension(AbstractCoreExtension):
    config_update_manager = None
    shared_config_data = None
    pids = None

    def init(self, core, app_directorys, appConfig, kwargs):
        manager = Manager()
        MultiprocessingCoreExtension.config_update_manager = manager
        MultiprocessingCoreExtension.shared_config_data = manager.dict()
        MultiprocessingCoreExtension.pids = manager.list()

        spell_directories = []
        nsFragments = ('agatsuma', 'spells', 'supplemental', 'mp')
        spell_directories.extend ([core._i_internal_spell_space(*nsFragments)
                            ])
        spell_directories.extend(kwargs.get('spell_directories', []))
        kwargs['spell_directories'] = spell_directories
        return (app_directorys, appConfig, kwargs)

    def additional_methods(self):
        return [("start_settings_updater", self.start_settings_updater),
                ("remember_pid", self.remember_pid),
                ("write_pid", self.write_pid)
                ]

    @staticmethod
    def name():
        return "multiprocessing"

    def on_core_post_configure(self, core):
        """
        spell_directories = []
        nsFragments = ('agatsuma', 'framework', 'tornado', 'spells')
        spell_directories.extend ([self._i_internal_spell_space(*nsFragments)
                            ])
        """
        MultiprocessingCoreExtension.removePidFile()
        log.mpcore.info("Calling pre-pool-init routines...")
        #self._pre_pool_init() # TODO: XXX:
        for spell in core.implementations_of(IPoolEventSpell):
            spell.pre_pool_init(core)

        core.pool = None
        workers = Settings.mpcore.workers
        if workers >= 0:
            log.mpcore.debug("Starting %d workers..." % workers)
            core.pool = Pool(processes=workers,
                             initializer = _worker_initializer,
                             initargs = (Settings.mpcore.settings_update_timeout, ))
        else:
            log.mpcore.info("Pool initiation skipped due negative workers count")

        log.mpcore.info("Calling post-pool-init routines...")
        for spell in core.implementations_of(IPoolEventSpell):
            spell.post_pool_init(core)
        self.pool = core.pool

    def on_core_stop(self, core):
        if core.pool:
            core.pool.close()
        self.removePidFile()

################################################
    # TODO: XXX: one method enough
    @staticmethod
    def remember_pid(pid):
        assert type(pid) is int
        MultiprocessingCoreExtension.pids.append(pid)

    @staticmethod
    def write_pid(pid):
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

    def start_settings_updater(self):
        """ Initiates periodic checking for config updates. May be overriden in
        subclasses """
        if self.pool:
            self._start_settings_updater()
        else:
            log.mpcore.info("Settings updater is not started in main thread due empty process' pool")

    def _start_settings_updater(self):
        raise EAbstractFunctionCall()

    @staticmethod
    def _update_settings():
        # Settings in current thread are in old state
        # If we detect, that shared object has updated config we replace it
        process = multiprocessing.current_process()
        thread = threading.currentThread()
        log.mpcore.info("Checking for config updates in process '%s' with PID %s using thread '%s'..."
                          % (str(process.name), process.pid, thread.getName()))

        prevUpdate = Settings.configData['update']
        lastUpdate = MultiprocessingCoreExtension.shared_config_data['update']
        if (prevUpdate < lastUpdate):
            process = multiprocessing.current_process()
            thread = threading.currentThread()
            log.mpcore.info("Process '%s' with PID %s received new config, updating using thread '%s'..."
                          % (str(process.name), process.pid, thread.getName()))
            #Core.settings.parse_settings(Core.shared_config_data['data'], Settings.descriptors)
            Settings.set_config_data(MultiprocessingCoreExtension.shared_config_data['data'], update_shared = False)

def _worker_initializer(timeout):
    process = multiprocessing.current_process()
    MultiprocessingCoreExtension.remember_pid(process.pid)
    MultiprocessingCoreExtension.write_pid(process.pid)
    log.mpcore.debug("Initializing worker process '%s' with PID %d. Starting config update checker with %ds timeout" % (str(process.name), process.pid, timeout))
    MPStandaloneExtension._update_settings_by_timer(timeout)

class MPStandaloneExtension(MultiprocessingCoreExtension):
    def _start_settings_updater(self):
        MPStandaloneExtension._update_settings_by_timer(Settings.mpcore.settings_update_timeout)

    @staticmethod
    def _update_settings_by_timer(timeout):
        if Core.instance.shutdown:
            return
        threading.Timer(timeout, MPStandaloneExtension._update_settings_by_timer, (timeout, )).start()
        MultiprocessingCoreExtension._update_settings()
