# -*- coding: utf-8 -*-

from agatsuma.minicache import EternalInvariant
from agatsuma.core import Core

def Spell(spell_id):
    """Helper function which returns spell with given name

    Arguments:
    - `spell_id`:
    """
    return Core.instance.spellbook.get(spell_id, None)

@EternalInvariant
def Implementations(interface):
    """Wrapper function for :meth:`agatsuma.core.Core.implementations_of`
    caches results with :class:`agatsuma.minicache.MiniCache`
    """
    return Core.instance.implementations_of(interface)
