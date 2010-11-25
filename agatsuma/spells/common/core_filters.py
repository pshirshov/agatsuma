# -*- coding: utf-8 -*-

from agatsuma import log
from agatsuma import Implementations

from agatsuma.interfaces import AbstractSpell, IInternalSpell
from agatsuma.interfaces import IFilteringSpell

from agatsuma.commons.types import Atom

class TextFiltersSpell(AbstractSpell, IInternalSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Text Filtering Core Spell',
                  'deps' : (Atom.agatsuma_core, )
                 }
        AbstractSpell.__init__(self, Atom.agatsuma_text_filters, config)
        self.filterStack = []

    #def pre_configure(self, core):
    #    core.filterStack = []

    def post_configure(self, core):
        spells = Implementations(IFilteringSpell)
        if not spells:
            log.core.info("Filtering spells not found")
            return
        log.core.info("Adding text filters into stack...")
        for spell in spells:
            filters = spell.filters_ist()
            if filters:
                for tfilter in filters:
                    self.filterStack.append(tfilter)
                    log.core.info('Added text filter %s from %s' % (str(tfilter), spell.spell_id()))
            #TODO: templating and this
            """
            filters = spell.global_filters_list()
            if filters:
                for tfilter in filters:
                    self.core.global_filters_list.append(tfilter)
                    log.core.info('Added global text filter %s from %s' % (str(tfilter), spell.spell_id()))
            """
        log.core.info("Text filters are set up")

    def apply(self, s):
        ret = s
        for flt in self.filterStack:
            ret = flt(ret)
        return ret
