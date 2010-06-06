# -*- coding: utf-8 -*-

from agatsuma.log import log

from agatsuma.interfaces import AbstractSpell, HandlingSpell
        
class CoreSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Core Spell',
                  'deps' : ()
                 }
        AbstractSpell.__init__(self, 'agatsuma_core', config)
        
    def preConfigure(self, core):
        core.registerOption("!core.debug", bool, "Debug mode")
        core.registerOption("!core.debug_level", int, "Debug level. Possible values: 0, 1 (debug message pump), 2 (debug threads)")
        core.registerOption("!core.workers", int, "Size of working processes pool")
        core.registerOption("!core.settings_update_timeout", int, "Update timeout for workers")
        core.registerOption("!core.pidfile", unicode, "File with PIDs of all Agatsuma's processes")

    def postConfigure(self, core):
        log.core.info("Initializing URI map..")
        spells = core._implementationsOf(HandlingSpell)
        if spells:
            for spell in spells:
                spell.initRoutes(core.URIMap)
            for spell in spells:
                spell.postInitRoutes(core.URIMap)
            log.core.info("URI map initialized")    
            #log.core.debug("URI map:\n%s" % '\n'.join(map(lambda x: str(x), self.core.URIMap)))
            log.core.debug("URI map:")  
            for p in core.URIMap:
                log.core.debug("* %s" % str(p))  
        else:
            raise Exception("Handling spells not found!")
        
class TornadoSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Tornado Spell',
                  'deps' : ()
                 }
        AbstractSpell.__init__(self, 'agatsuma_tornado', config)
        
    def preConfigure(self, core):
        core.registerOption("!tornado.port", int, "Web server port")
        core.registerOption("!tornado.message_pump_timeout", int, "Message pushing interval")
        core.registerOption("!tornado.logger_pump_timeout", int, "Logging output interval")
