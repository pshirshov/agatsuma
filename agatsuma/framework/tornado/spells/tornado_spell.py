# -*- coding: utf-8 -*-

from agatsuma.log import log

from agatsuma.interfaces import AbstractSpell

class TornadoSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Tornado Spell',
                  'deps' : ()
                 }
        AbstractSpell.__init__(self, 'agatsuma_tornado', config)
        
    def preConfigure(self, core):
        core.registerOption("!tornado.port", int, "Web server port")
        core.registerOption("!tornado.cookie_secret", unicode, "cookie secret")
        core.registerOption("!tornado.parameters", dict, "Kwarg parameters for tornado application")
        core.registerOption("!tornado.message_pump_timeout", int, "Message pushing interval (msec)")
        core.registerOption("!tornado.logger_pump_timeout", int, "Logging output interval (msec)")
