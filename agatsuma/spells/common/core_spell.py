# -*- coding: utf-8 -*-

from agatsuma.interfaces import AbstractSpell, IInternalSpell, ISetupSpell

from agatsuma.elements import Atom

class CoreSpell(AbstractSpell, IInternalSpell, ISetupSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Core Spell',
                  'deps' : (),
                  'eager_unload' : True,
                 }
        AbstractSpell.__init__(self, Atom.agatsuma_core, config)

    def pre_configure(self, core):
        core.register_option("!core.debug", bool, "Debug mode")
        core.register_option("!core.debug_level", int, "Debug level. Possible values: 0, 1 (debug message pump), 2 (debug threads)")
        core.register_option("!logging.levels", dict, "Logging levels for loggers instantiated by Agatsuma")
        #core.register_option("!logging.formatters", dict, "Format strings for loggers instantiated by Agatsuma")
        core.register_option("!logging.named_levels", dict, "Logging levels for named loggers")
        core.register_option("!logging.root_level", unicode, "Logging level for root handler")
        core.register_option("!logging.default_level", unicode, "Default logging level")

    def requirements(self):
        return {"autodoc" : ["Sphinx>=0.6.5"],
               }
