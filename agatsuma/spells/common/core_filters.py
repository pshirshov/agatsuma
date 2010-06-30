# -*- coding: utf-8 -*-

from agatsuma import log
from agatsuma import Implementations

from agatsuma.interfaces import AbstractSpell
from agatsuma.interfaces import FilteringSpell

class TextFiltersSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Text Filtering Core Spell',
                  'deps' : ("agatsuma_core", )
                 }
        AbstractSpell.__init__(self, 'agatsuma_text_filters', config)
        self.filterStack = []

    #def preConfigure(self, core):
    #    core.filterStack = []

    def postConfigure(self, core):
        spells = Implementations(FilteringSpell)
        if not spells:
            log.core.info("Filtering spells not found")
            return
        log.core.info("Adding text filters into stack...")
        for spell in spells:
            filters = spell.filtersList()
            if filters:
                for tfilter in filters:
                    self.filterStack.append(tfilter)
                    log.core.info('Added text filter %s from %s' % (str(tfilter), spell.spellId()))
            #TODO: templating and this
            """
            filters = spell.globalFiltersList()
            if filters:
                for tfilter in filters:
                    self.core.globalFilterStack.append(tfilter)
                    log.core.info('Added global text filter %s from %s' % (str(tfilter), spell.spellId()))
            """
        log.core.info("Text filters are set up")

    def apply(self, s):
        ret = s
        for flt in self.filterStack:
            ret = flt(ret)
        return ret
