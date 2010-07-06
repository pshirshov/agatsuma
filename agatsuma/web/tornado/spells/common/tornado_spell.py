# -*- coding: utf-8 -*-

from agatsuma.log import log

from agatsuma.interfaces import AbstractSpell
from agatsuma.web.tornado.interfaces import HandlingSpell
from agatsuma.web.tornado import Url

class TornadoSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Tornado Spell',
                  'deps' : (),
                  'eager_unload' : True,
                 }
        AbstractSpell.__init__(self, 'agatsuma_tornado', config)

    def preConfigure(self, core):
        log.newLogger("tcore")
        core.registerOption("!tornado.port", int, "Web server port")
        core.registerOption("!tornado.logger_pump_timeout", int, "Logging output interval (msec)")
        core.registerOption("!tornado.xheaders", bool, "Support the X-Real-Ip and X-Scheme headers")
        core.registerOption("!tornado.ssl_parameters", dict, "SSL options dictionary for tornado http server")
