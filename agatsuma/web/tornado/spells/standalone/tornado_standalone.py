# -*- coding: utf-8 -*-

from agatsuma.log import log

from agatsuma.interfaces import AbstractSpell, InternalSpell, SetupSpell
from agatsuma.interfaces import PoolEventSpell
from agatsuma.web.tornado.interfaces import HandlingSpell
from agatsuma.web.tornado import Url

class TornadoSpell(AbstractSpell, InternalSpell, SetupSpell, PoolEventSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Tornado Spell',
                  'deps' : (),
                  'eager_unload' : True,
                 }
        AbstractSpell.__init__(self, 'agatsuma_tornado_standalone', config)

    def preConfigure(self, core):
        log.newLogger("tcore")
        core.registerOption("!tornado.cookie_secret", unicode, "cookie secret")
        core.registerOption("!tornado.message_pump_timeout", int, "Message pushing interval (msec)")
        core.registerOption("!tornado.app_parameters", dict, "Kwarg parameters for tornado application")

    def __processURL(self, core, url):
        if type(url) is tuple:
            return url
        if type(url) is Url:
            core.URITemplates[url.name] = url.template
            return (url.regex, url.handler)
        raise Exception("Incorrect URL data^ %s" % str(url))

    def postConfigure(self, core):
        log.tcore.info("Initializing URI map..")
        spells = core.implementationsOf(HandlingSpell)
        if spells:
            urimap = []
            for spell in spells:
                spell.initRoutes(urimap)
            for spell in spells:
                spell.postInitRoutes(urimap)
            core.URIMap = []
            core.URITemplates = {}
            for url in urimap:
                core.URIMap.append(self.__processURL(core, url))
            log.tcore.info("URI map initialized")
            #log.tcore.debug("URI map:\n%s" % '\n'.join(map(lambda x: str(x), self.core.URIMap)))
            log.tcore.debug("URI map:")
            for p in core.URIMap:
                log.tcore.debug("* %s" % str(p))
        else:
            raise Exception("Handling spells not found!")

    def prePoolInit(self, core):
        # Check if message pump is required for some of controllers
        core.messagePumpNeeded = False
        from agatsuma.web.tornado import MsgPumpHandler
        for uri, handler in core.URIMap:
            if issubclass(handler, MsgPumpHandler):
                core.messagePumpNeeded = True
                core.waitingCallbacks = []
                break

    def requirements(self):
        return {"tornado" : ["tornado>=0.2"],
               }
