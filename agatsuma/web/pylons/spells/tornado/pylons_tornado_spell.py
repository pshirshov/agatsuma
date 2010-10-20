# -*- coding: utf-8 -*-

#from agatsuma.log import log

from agatsuma.interfaces import AbstractSpell, InternalSpell

class PylonsWSGISpell(AbstractSpell, InternalSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Pylons/Tornado Spell',
                  'deps' : ('agatsuma_tornado', ),
                  'eager_unload' : True,
                 }
        AbstractSpell.__init__(self, 'agatsuma_pylons_tornado', config)

    def pre_configure(self, core):
        pass
        #TODO: options? This problem belongs to application for now
