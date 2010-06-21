# -*- coding: utf-8 -*-

class StorageSpell(object):
    """ This interface is mix-in that whould be added
    to all the spells that are responsible to communication
    with different data storages (databases or memcache service for
    example)
    
    This interface doesn't contain any methods for now because
    all work may be done in
    :meth:`agatsuma.interfaces.abstract_spell.AbstractSpell.preConfigure`
    :meth:agatsuma.interfaces.abstract_spell.AbstractSpell.postConfigure`
    methods. So this interface was introduced only for ordering
    purposes.
    """
    pass
