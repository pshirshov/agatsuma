# -*- coding: utf-8 -*-

import threading
import multiprocessing
from multiprocessing import Pool, Manager

from agatsuma import Settings, log
from agatsuma.core import Core
from agatsuma.interfaces import PoolEventSpell

"""
Warning: common core is only able to propagate settings update to process 
         pool. 
         Updating settings in main thread is subclass' problem
"""

def updateSettings():
    # Settings in current thread is in old state
    # If we detect, that shared object has updated config we replace it
    prevUpdate = Settings.configData['update']
    lastUpdate = MPCore.sharedConfigData['update']
    if (prevUpdate < lastUpdate):
        process = multiprocessing.current_process()
        log.core.info("Process '%s' with PID %s received new config, updating..." % (str(process.name), process.pid))
        #Core.settings.parseSettings(Core.sharedConfigData['data'], Settings.descriptors)
        Settings.setConfigData(MPCore.sharedConfigData['data'], updateShared = False)

def updateSettingsByTimer(timeout):
    threading.Timer(timeout, updateSettingsByTimer, (timeout, )).start()    
    updateSettings()
    
def workerInitializer(timeout):
    process = multiprocessing.current_process()
    Core.instance.writePid(process.pid)
    MPCore.rememberPid(process.pid)
    log.core.debug("Initializing worker process '%s' with PID %d. Starting config update checker with %ds timeout" % (str(process.name), process.pid, timeout))
    updateSettingsByTimer(timeout)

class MPCore(Core):
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
        Core.__init__(self, appDir, appConfig, **kwargs)
    
    def _postConfigure(self):
        log.core.info("Calling pre-pool-init routines...")
        self._prePoolInit()
        for spell in self._implementationsOf(PoolEventSpell):
            spell.prePoolInit(self)

        self.pool = None
        workers = Settings.core.workers
        if workers >= 0:
            log.core.debug("Starting %d workers..." % workers)
            self.pool = Pool(processes=workers, 
                             initializer = workerInitializer, 
                             initargs = (Settings.core.settings_update_timeout, ))
        else:
            log.core.info("Pool initiation skipped due negative workers count")
            
        log.core.info("Calling post-pool-init routines...")
        for spell in self._implementationsOf(PoolEventSpell):
            spell.postPoolInit(self)
        
    def _prePoolInit(self):
        pass

    @staticmethod
    def rememberPid(pid):
        assert type(pid) is int
        MPCore.pids.append(pid)
