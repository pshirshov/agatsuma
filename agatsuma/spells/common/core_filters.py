# -*- coding: utf-8 -*-

from agatsuma.log import log

from agatsuma.interfaces.abstract_spell import AbstractSpell
from agatsuma.interfaces.filtering_spell import FilteringSpell
        
class TextFiltersSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Text Filtering Core Spell',
                  'deps' : ("agatsuma_core", )
                 }
        AbstractSpell.__init__(self, 'agatsuma_text_filters', config)

    def postConfigure(self, core):
        spells = core._implementationsOf(FilteringSpell)
        if not spells:
            log.core.info("Filtering spells not found")
            return
        log.core.info("Adding text filters into stack...")
        for spell in spells:
            filters = spell.filtersList()
            if filters:
                for tfilter in filters:
                    core.filterStack.append(tfilter)
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