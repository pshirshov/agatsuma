# -*- coding: utf-8 -*-

from multiprocessing import Queue as MPQueue

from agatsuma.log import log

from agatsuma.interfaces import AbstractSpell, InternalSpell, SetupSpell
from agatsuma.interfaces import PoolEventSpell
from agatsuma.web.tornado.interfaces import HandlingSpell
from agatsuma.web.tornado import Url

from agatsuma.elements import Atom

class TornadoSpell(AbstractSpell, InternalSpell, SetupSpell, PoolEventSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Tornado Spell',
                  'deps' : (),
                  'eager_unload' : True,
                 }
        AbstractSpell.__init__(self, Atom.agatsuma_tornado_standalone, config)

    def pre_configure(self, core):
        log.new_logger("tcore")
        core.register_option("!tornado.cookie_secret", unicode, "cookie secret")
        core.register_option("!tornado.message_pump_timeout", int, "Message pushing interval (msec)")
        core.register_option("!tornado.app_parameters", dict, "Kwarg parameters for tornado application")

    def __process_url(self, core, url):
        if type(url) is tuple:
            return url
        if type(url) is Url:
            core.URITemplates[url.name] = url.template
            return (url.regex, url.handler)
        raise Exception("Incorrect URL data^ %s" % str(url))

    def post_configure(self, core):
        log.tcore.info("Initializing URI map..")
        spells = core.implementations_of(HandlingSpell)
        if spells:
            urimap = []
            for spell in spells:
                spell.init_routes(urimap)
            for spell in spells:
                spell.post_init_routes(urimap)
            core.URIMap = []
            core.URITemplates = {}
            for url in urimap:
                core.URIMap.append(self.__process_url(core, url))
            log.tcore.info("URI map initialized")
            #log.tcore.debug("URI map:\n%s" % '\n'.join(map(lambda x: str(x), self.core.URIMap)))
            log.tcore.debug("URI map:")
            for p in core.URIMap:
                log.tcore.debug("* %s" % str(p))
        else:
            raise Exception("Handling spells not found!")

    def pre_pool_init(self, core):
        # Check if message pump is required for some of controllers
        core.messagePumpNeeded = False
        from agatsuma.web.tornado import MsgPumpHandler
        for uri, handler in core.URIMap:
            if issubclass(handler, MsgPumpHandler):
                core.messagePumpNeeded = True
                core.waitingCallbacks = []
                break
        if core.messagePumpNeeded:
            core.mqueue = MPQueue()

    def requirements(self):
        return {"tornado" : ["tornado>=0.2"],
               }
