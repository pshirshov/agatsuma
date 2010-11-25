# -*- coding: utf-8 -*-

from agatsuma import Settings, log
from agatsuma.core import MultiprocessingCoreExtension

from agatsuma.interfaces import AbstractSpell, IInternalSpell

from agatsuma.commons.types import Atom

class MPCoreSpell(AbstractSpell, IInternalSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Multiprocessing Core Spell',
                  'deps' : (),
                 }
        AbstractSpell.__init__(self, Atom.agatsuma_mp_core, config)

    def pre_configure(self, core):
        #import logging
        log.new_logger("mpcore")
        core.register_option("!mpcore.workers", int, "Size of working processes pool. Negative to disable")
        core.register_option("!mpcore.settings_update_timeout", int, "Update timeout for workers (sec)")
        core.register_option("!mpcore.pidfile", unicode, "File with PIDs of all Agatsuma's processes")

    def post_config_update(self, **kwargs):
        if kwargs.get('update_shared', True):
            log.mpcore.info("Propagating new config data to another processes")
            MultiprocessingCoreExtension.shared_config_data.update(Settings.configData)
