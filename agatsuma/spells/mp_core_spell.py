# -*- coding: utf-8 -*-

from agatsuma import log, Settings
from agatsuma.core import MPCore

from agatsuma.interfaces import AbstractSpell
        
class MPCoreSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Multiprocessing Core Spell',
                  'deps' : ()
                 }
        AbstractSpell.__init__(self, 'agatsuma_mp_core', config)
        
    def preConfigure(self, core):
        core.registerOption("!core.workers", int, "Size of working processes pool. Negative to disable")
        core.registerOption("!core.settings_update_timeout", int, "Update timeout for workers (sec)")
        core.registerOption("!core.pidfile", unicode, "File with PIDs of all Agatsuma's processes")

    def postConfigUpdate(self, **kwargs):
        if kwargs.get('updateShared', True):
            log.core.info("Propagating new config data to another processes")
            MPCore.sharedConfigData.update(Settings.configData)

