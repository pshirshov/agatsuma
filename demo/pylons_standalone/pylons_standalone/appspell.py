# -*- coding: utf-8 -*-

from agatsuma.interfaces import AbstractSpell, SetupSpell
from agatsuma.web.pylons.interfaces import HandlingSpell

class DemoAppSpell(AbstractSpell, SetupSpell, HandlingSpell):
    def __init__(self):
        config = {'info' : 'Pylons Standalone Demoapp Spell',
                  'deps' : (),
                 }
        AbstractSpell.__init__(self, 'demoapp_spell', config)

    def preConfigure(self, core):
        pass
        #log.newLogger("pcore")
        #core.registerOption("!tornado.cookie_secret", unicode, "cookie secret")
        #core.registerOption("!tornado.message_pump_timeout", int, "Message pushing interval (msec)")
        #core.registerOption("!tornado.app_parameters", dict, "Kwarg parameters for tornado application")


    def requirements(self):
        return {}
              #{"agatsuma" : ["agatsuma>=0.1"], }

    def pyEntryPoints(self):
        return {'paste.app_factory' : [('main', 'pylons_demo', 'make_app'), ],
                'paste.app_install' : [('main', 'pylons.util', 'PylonsInstaller'), ],
        }

    def initRoutes(self, map):
        map.connect('/{controller}/{action}')
        map.connect('/{controller}/{action}/{id}')
