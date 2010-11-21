# -*- coding: utf-8 -*-

from agatsuma.log import log
from agatsuma.elements import Atom

from agatsuma.interfaces import AbstractSpell

class SimpleSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Simple demo spell',
                  'deps' : ()
                 }
        AbstractSpell.__init__(self, Atom.demo_spell, config)

    def entry_point(self, *args, **kwargs):
        log.core.info("Demo entry point called with argv %s" % str(args))

    def pre_configure(self, core):
        core.register_option("!test.rotest", unicode, "Test read-only setting")
        core.register_option("test.test", unicode, "Test setting")
        core.register_entry_point("demoPoint", self.entry_point)
