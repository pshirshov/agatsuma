# -*- coding: utf-8 -*-

from agatsuma.interfaces import AbstractSpell, SetupSpell
from agatsuma.web.pylons.interfaces import HandlingSpell

class DemoAppSpell(AbstractSpell, SetupSpell, HandlingSpell):
    def __init__(self):
        config = {'info' : 'Pylons-Tornado Demoapp Spell',
                  'deps' : (),
                 }
        AbstractSpell.__init__(self, 'demoapp_spell', config)

    def preConfigure(self, core):
        core.registerOption("!pylons.app", dict, "dev.ini equivalent")
        core.registerOption("!pylons.glob", dict, "dev.ini equivalent")
        core.registerOption("!pylons.full_stack", bool, "pylons parameter")
        core.registerOption("!pylons.static_files", bool, "pylons parameter")
        
    def requirements(self):
        return {}
              #{"agatsuma" : ["agatsuma>=0.1"], }

    def initRoutes(self, map):
        map.connect('/{controller}/{action}')
        map.connect('/{controller}/{action}/{id}')
