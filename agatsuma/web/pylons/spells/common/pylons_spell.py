# -*- coding: utf-8 -*-

from agatsuma.log import log

from agatsuma.interfaces import AbstractSpell, InternalSpell, SetupSpell

class PylonsSpell(AbstractSpell, InternalSpell, SetupSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Pylons Spell',
                  'deps' : (),
                  'eager_unload' : True,
                 }
        AbstractSpell.__init__(self, 'agatsuma_pylons', config)

    def preConfigure(self, core):
        log.new_logger("pcore")
        #core.registerOption("!tornado.cookie_secret", unicode, "cookie secret")
        #core.registerOption("!tornado.message_pump_timeout", int, "Message pushing interval (msec)")
        #core.registerOption("!tornado.app_parameters", dict, "Kwarg parameters for tornado application")


    def requirements(self):
        return {"pylons" : ["pylons>=1.0"],
               }
