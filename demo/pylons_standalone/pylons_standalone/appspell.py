# -*- coding: utf-8 -*-

from agatsuma.interfaces import AbstractSpell, SetupSpell
from agatsuma.web.pylons.interfaces import HandlingSpell

class DemoAppSpell(AbstractSpell, SetupSpell, HandlingSpell):
    def __init__(self):
        config = {'info' : 'Pylons Standalone Demoapp Spell',
                  'deps' : (),
                 }
        AbstractSpell.__init__(self, 'demoapp_spell', config)

    def pre_configure(self, core):
        pass
        #log.new_logger("pcore")
        #core.register_option("!tornado.cookie_secret", unicode, "cookie secret")
        #core.register_option("!tornado.message_pump_timeout", int, "Message pushing interval (msec)")
        #core.register_option("!tornado.app_parameters", dict, "Kwarg parameters for tornado application")


    def requirements(self):
        return {}
              #{"agatsuma" : ["agatsuma>=0.1"], }

    def py_entry_points(self):
        return {'paste.app_factory' : [('main', 'pylons_demo', 'make_app'), ],
                'paste.app_install' : [('main', 'pylons.util', 'PylonsInstaller'), ],
        }

    def init_routes(self, map):
        map.connect('/{controller}/{action}')
        map.connect('/{controller}/{action}/{id}')
