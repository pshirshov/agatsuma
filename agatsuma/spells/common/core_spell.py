# -*- coding: utf-8 -*-

from agatsuma.interfaces import AbstractSpell, InternalSpell, SetupSpell

class CoreSpell(AbstractSpell, InternalSpell, SetupSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Core Spell',
                  'deps' : (),
                  'eager_unload' : True,
                 }
        AbstractSpell.__init__(self, 'agatsuma_core', config)

    def preConfigure(self, core):
        core.registerOption("!core.debug", bool, "Debug mode")
        core.registerOption("!core.debug_level", int, "Debug level. Possible values: 0, 1 (debug message pump), 2 (debug threads)")
        core.registerOption("!logging.levels", dict, "Logging levels for loggers instantiated by Agatsuma")
        #core.registerOption("!logging.formatters", dict, "Format strings for loggers instantiated by Agatsuma")
        core.registerOption("!logging.named_levels", dict, "Logging levels for named loggers")
        core.registerOption("!logging.root_level", unicode, "Logging level for root handler")
        core.registerOption("!logging.default_level", unicode, "Default logging level")

    def requirements(self):
        return {"autodoc" : ["Sphinx>=0.6.5"],
               }
