# -*- coding: utf-8 -*-

from agatsuma.log import log

from agatsuma.elements import Atom

from agatsuma.interfaces import AbstractSpell, IInternalSpell

class TornadoSpell(AbstractSpell, IInternalSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Tornado Spell',
                  'deps' : (),
                  'eager_unload' : True,
                 }
        AbstractSpell.__init__(self, Atom.agatsuma_tornado, config)

    def pre_configure(self, core):
        log.new_logger("tcore")
        core.register_option("!tornado.port", int, "Web server port")
        core.register_option("!tornado.logger_pump_timeout", int, "Logging output interval (msec)")
        core.register_option("!tornado.xheaders", bool, "Support the X-Real-Ip and X-Scheme headers")
        core.register_option("!tornado.ssl_parameters", dict, "SSL options dictionary for tornado http server")
