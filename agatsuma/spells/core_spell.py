# -*- coding: utf-8 -*-

from agatsuma import log

from agatsuma.interfaces import AbstractSpell
        
class CoreSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Core Spell',
                  'deps' : ()
                 }
        AbstractSpell.__init__(self, 'agatsuma_core', config)
        
    def preConfigure(self, core):
        core.registerOption("!core.debug", bool, "Debug mode")
        core.registerOption("!core.debug_level", int, "Debug level. Possible values: 0, 1 (debug message pump), 2 (debug threads)")
