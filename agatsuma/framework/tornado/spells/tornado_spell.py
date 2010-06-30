# -*- coding: utf-8 -*-

from agatsuma.log import log

from agatsuma.interfaces import AbstractSpell
from agatsuma.framework.tornado.interfaces import HandlingSpell
from agatsuma.framework.tornado import Url

class TornadoSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Tornado Spell',
                  'deps' : (),
                  'eager_unload' : True,
                 }
        AbstractSpell.__init__(self, 'agatsuma_tornado', config)

    def preConfigure(self, core):
        import logging
        log.newLogger("tcore")
        core.registerOption("!tornado.port", int, "Web server port")
        core.registerOption("!tornado.cookie_secret", unicode, "cookie secret")
        core.registerOption("!tornado.app_parameters", dict, "Kwarg parameters for tornado application")
        core.registerOption("!tornado.ssl_parameters", dict, "SSL options dictionary for tornado http server")
        core.registerOption("!tornado.message_pump_timeout", int, "Message pushing interval (msec)")
        core.registerOption("!tornado.logger_pump_timeout", int, "Logging output interval (msec)")
        core.registerOption("!tornado.xheaders", bool, "Support the X-Real-Ip and X-Scheme headers")

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

    def requirements(self):
        return {"tornado" : ["tornado>=0.2"],
               }
