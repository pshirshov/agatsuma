# -*- coding: utf-8 -*-

from agatsuma.log import log

from agatsuma.interfaces import AbstractSpell

class PylonsWSGISpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Pylons/Tornado Spell',
                  'deps' : (''),
                  'eager_unload' : True,
                 }
        AbstractSpell.__init__(self, 'agatsuma_pylons_tornado', config)

    def preConfigure(self, core):
        pass
        #TODO: options
        #log.newLogger("tcore")
        #core.registerOption("!tornado.cookie_secret", unicode, "cookie secret")
        #core.registerOption("!tornado.message_pump_timeout", int, "Message pushing interval (msec)")
        #core.registerOption("!tornado.app_parameters", dict, "Kwarg parameters for tornado application")
