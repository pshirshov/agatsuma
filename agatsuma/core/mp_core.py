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
from agatsuma.core import Core
from agatsuma.interfaces import PoolEventSpell
 
def _workerInitializer(timeout):
    process = multiprocessing.current_process()
    MPCore.writePid(process.pid)
    MPCore.rememberPid(process.pid)
    log.mpcore.debug("Initializing worker process '%s' with PID %d. Starting config update checker with %ds timeout" % (str(process.name), process.pid, timeout))
    MPCore._updateSettingsByTimer(timeout)

class MPCore(Core):
    """ Base core extension providing pool of worker processes and able to
notify them about settings changes.

TODO: startSettinsUpdater(self)

.. warning:: common core is only able to propagate settings update to process pool. Updating settings in main thread is subclass' problem.
    """
    configUpdateManager = Manager()
    sharedConfigData = configUpdateManager.dict()
    pids = configUpdateManager.list()
    
    def __init__(self, appDir, appConfig, **kwargs):
        """
        
        Arguments:
        - `self`:
        - `appDir`:
        - `appConfig`:
        """
        spellsDirs = []
        nsFragments = ('agatsuma', 'spells', 'supplemental', 'mp')
        spellsDirs.extend ([self._internalSpellSpace(*nsFragments)
                            ])
        spellsDirs.extend(kwargs.get('spellsDirs', []))
        kwargs['spellsDirs'] = spellsDirs
        Core.__init__(self, appDir, appConfig, **kwargs)
    
    def _postConfigure(self):
        spellsDirs = []
        nsFragments = ('agatsuma', 'framework', 'tornado', 'spells')
        spellsDirs.extend ([self._internalSpellSpace(*nsFragments)
                            ])
        
        MPCore.removePidFile()
        log.mpcore.info("Calling pre-pool-init routines...")
        self._prePoolInit()
        for spell in self._implementationsOf(PoolEventSpell):
            spell.prePoolInit(self)

        self.pool = None
        workers = Settings.mpcore.workers
        if workers >= 0:
            log.mpcore.debug("Starting %d workers..." % workers)
            self.pool = Pool(processes=workers, 
                             initializer = _workerInitializer, 
                             initargs = (Settings.mpcore.settings_update_timeout, ))
        else:
            log.mpcore.info("Pool initiation skipped due negative workers count")

        log.mpcore.info("Calling post-pool-init routines...")
        for spell in self._implementationsOf(PoolEventSpell):
            spell.postPoolInit(self)

    def _prePoolInit(self):
        pass

    def _stop(self):
        if self.pool:
            self.pool.close()
        self.removePidFile()

    @staticmethod
    def rememberPid(pid):
        assert type(pid) is int
        MPCore.pids.append(pid)

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

    def startSettinsUpdater(self):
        MPCore._updateSettingsByTimer()

    @staticmethod
    def _updateSettings():
        # Settings in current thread are in old state
        # If we detect, that shared object has updated config we replace it
        prevUpdate = Settings.configData['update']
        lastUpdate = MPCore.sharedConfigData['update']
        if (prevUpdate < lastUpdate):
            process = multiprocessing.current_process()
            thread = threading.currentThread()
            log.mpcore.info("Process '%s' with PID %s received new config, updating using thread '%s'..."
                          % (str(process.name), process.pid, thread.getName()))
            #Core.settings.parseSettings(Core.sharedConfigData['data'], Settings.descriptors)
            Settings.setConfigData(MPCore.sharedConfigData['data'], updateShared = False)

    @staticmethod
    def _updateSettingsByTimer(timeout):
        threading.Timer(timeout, MPCore._updateSettingsByTimer, (timeout, )).start()    
        MPCore._updateSettings()
