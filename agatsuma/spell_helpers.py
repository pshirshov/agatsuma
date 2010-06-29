# -*- coding: utf-8 -*-

from agatsuma.core import Core

def Spell(spellId):
    """Helper function which returns spell with given name

    Arguments:
    - `spellId`:
    """
    return Core.instance.spellsDict.get(spellId, None)

def Implementations(interface):
    """Wrapper function for :meth:`agatsuma.core.Core.implementationsOf`

    Arguments:
    - `interface`:
    """
    return Core.instance.implementationsOf(interface)

'''
class Spell(object):
    """Provides quick access to spell with given name
    """

    def __init__(self, spellId):
        """

        Arguments:
        - `spellId`:
        """
        self._spell = Core.instance.spellsDict[spellId]

    def __call__(self):
        return self._spell

class Implementations(object):
    """Provides quick access to :meth:`agatsuma.core.Core.implementationsOf`
    """

    def __init__(self, interface):
        """
        """
        self._implementations = Core.instance.implementationsOf(interface)

    def __call__(self):
        return self._implementations
'''
