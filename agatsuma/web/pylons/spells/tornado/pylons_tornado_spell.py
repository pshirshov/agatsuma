# -*- coding: utf-8 -*-

#from agatsuma.log import log

from agatsuma.interfaces import AbstractSpell, IInternalSpell

from agatsuma.elements import Atom

class PylonsWSGISpell(AbstractSpell, IInternalSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Pylons/Tornado Spell',
                  'deps' : (Atom.agatsuma_tornado, ),
                  'eager_unload' : True,
                 }
        AbstractSpell.__init__(self, Atom.agatsuma_pylons_tornado, config)

    def pre_configure(self, core):
        pass
        #TODO: options? This problem belongs to application for now
