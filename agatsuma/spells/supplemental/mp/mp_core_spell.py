# -*- coding: utf-8 -*-

from agatsuma import Settings, log
from agatsuma.core import MPCore

from agatsuma.interfaces import AbstractSpell

class MPCoreSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Multiprocessing Core Spell',
                  'deps' : (),
                 }
        AbstractSpell.__init__(self, 'agatsuma_mp_core', config)

    def preConfigure(self, core):
        import logging
        log.newLogger("mpcore", logging.DEBUG)
        core.registerOption("!mpcore.workers", int, "Size of working processes pool. Negative to disable")
        core.registerOption("!mpcore.settings_update_timeout", int, "Update timeout for workers (sec)")
        core.registerOption("!mpcore.pidfile", unicode, "File with PIDs of all Agatsuma's processes")

    def postConfigUpdate(self, **kwargs):
        if kwargs.get('updateShared', True):
            log.mpcore.info("Propagating new config data to another processes")
            MPCore.sharedConfigData.update(Settings.configData)

