# -*- coding: utf-8 -*-

from agatsuma.minicache import EternalInvariant
from agatsuma.core import Core
from agatsuma.elements import to_atom, is_atom

def Spell(spell_id):
    """Helper function which returns spell with given name (name should be an atom)

    Arguments:
    - `spell_id`:
    """
    assert is_atom(spell_id)
    return Core.instance.spellbook.get(spell_id, None)

def SpellByStr(spell_id):
    """Helper function which returns spell with given name

    Arguments:
    - `spell_id`:
    """
    return Core.instance.spellbook.get(to_atom(spell_id), None)


@EternalInvariant
def Implementations(interface):
    """Wrapper function for :meth:`agatsuma.core.Core.implementations_of`
    caches results with :class:`agatsuma.minicache.MiniCache`
    """
    return Core.instance.implementations_of(interface)
