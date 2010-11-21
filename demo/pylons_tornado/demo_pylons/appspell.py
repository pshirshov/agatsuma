# -*- coding: utf-8 -*-

from agatsuma.interfaces import AbstractSpell, SetupSpell

from agatsuma.elements import Atom

from agatsuma.web.pylons.interfaces import HandlingSpell

class DemoAppSpell(AbstractSpell, SetupSpell, HandlingSpell):
    def __init__(self):
        config = {'info' : 'Pylons-Tornado Demoapp Spell',
                  'deps' : (),
                 }
        AbstractSpell.__init__(self, Atom.demoapp_spell, config)

    def pre_configure(self, core):
        core.register_option("!pylons.app", dict, "dev.ini equivalent")
        core.register_option("!pylons.glob", dict, "dev.ini equivalent")
        core.register_option("!pylons.full_stack", bool, "pylons parameter")
        core.register_option("!pylons.static_files", bool, "pylons parameter")

    def requirements(self):
        return {}
              #{"agatsuma" : ["agatsuma>=0.1"], }

    def init_routes(self, map):
        map.connect('/{controller}/{action}')
        map.connect('/{controller}/{action}/{id}')
