# -*- coding: utf-8 -*-

class Spellbook(object):
    """
    """
    
    def __init__(self):
        """
        """

        self.__spellsdict = {}
        self.__spellslist = []

    def get(self, spell_id):
        return self.__spellsdict.get(spell_id, None)

    def register(self, spell):
        self.__spellslist.append(spell)
        self.__spellsdict[spell.spell_id()] = spell

    def eliminate(self, spell):
        self.__spellslist.remove(spell)
        del self.__spellsdict[spell.spell_id()]

    def all_names(self):
        return map(lambda p: str(p.spell_id()), self.__spellslist)

    def to_list(self):
        return self.__spellslist

    def implementations_of(self, InterfaceClass):
        """ The most important function for Agatsuma-based application.
        It returns all the spells implementing interface `InterfaceClass`.
        """
        return filter(lambda spell: issubclass(type(spell), InterfaceClass),
                      self.__spellslist)

