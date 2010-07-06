# -*- coding: utf-8 -*-

from agatsuma.core import Core
from agatsuma.settings import Settings
from agatsuma.log import log

from agatsuma.interfaces import AbstractSpell

class SimpleSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Simple demo spell',
                  'deps' : ()
                 }
        AbstractSpell.__init__(self, 'demo_spell', config)

    def entryPoint(self, *args, **kwargs):
        log.core.info("Demo entry point called with argv %s" % str(args))

    def preConfigure(self, core):
        core.registerOption("!test.rotest", unicode, "Test read-only setting")
        core.registerOption("test.test", unicode, "Test setting")
        core.registerEntryPoint("demoPoint", self.entryPoint)
