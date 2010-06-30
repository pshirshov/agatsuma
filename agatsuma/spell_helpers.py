# -*- coding: utf-8 -*-

from agatsuma.minicache import EternalInvariant
from agatsuma.core import Core

def Spell(spellId):
    """Helper function which returns spell with given name

    Arguments:
    - `spellId`:
    """
    return Core.instance.spellsDict.get(spellId, None)

@EternalInvariant
def Implementations(interface):
    """Wrapper function for :meth:`agatsuma.core.Core.implementationsOf`
    caches results with :class:`agatsuma.minicache.MiniCache`
    """
    return Core.instance.implementationsOf(interface)
