#!/bin/env python

"""
This module provides ability to emulate classic atoms in Python.
Atoms are types which have only comparison operation and (optionally)
may be converted to string. Two atoms declared in different places are
same and thats all.

>>> atom1 = Atom.myatom
>>> atom2 = Atom.myatom
>>> atom1 == atom2
True
>>> atom3 = Atom.another_atom
>>> atom1 == atom3
False
>>> atom3 == 1
False
>>> atom3 == "atom3"
False
>>> test_dict = {}
>>> test_dict[Atom.keyatom] = "test"
>>> test_dict[Atom.keyatom] == "test"
True
>>> test_dict["keyatom"]
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
KeyError: 'keyatom'
>>> is_atom(atom1)
True
>>> is_atom("not an atom")
False
>>> atom1()
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
CantInstantiateAtom
>>> Atom.test="lol"
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
CantChangeAtom
"""

class AtomFabric(type):
    class AtomImplementation(type):
        def __eq__(self, other):
            if type(other) == AtomFabric.AtomImplementation:
                return self.__name__ == other.__name__
            return type.__eq__(self, other)

        def __ne__(self, other):
            return not self.__eq__(other)

        def __repr__(self):
            return "<atom %s>" % self.__name__

        def __str__(self):
            return self.__name__

        def __hash__(self):
            return str.__hash__(self.__name__)

    class CantInstantiateAtom(Exception):
        pass

    class AtomInstantiationPreventor(type):
        def __new__(*args, **kwargs):
            raise AtomFabric.CantInstantiateAtom()

    def __getattribute__(self, name):
        return to_atom(name)

    class CantChangeAtom(Exception):
        pass

    def __setattr__(self, name, value):
        raise AtomFabric.CantChangeAtom()

# Public entities
class Atom(object):
    __metaclass__ = AtomFabric

def is_atom(entity):
    return isinstance(entity, AtomFabric.AtomImplementation)

def to_atom(name):
    assert isinstance(name, str) or isinstance(name, unicode)
    return type.__new__(AtomFabric.AtomImplementation,
                        str(name),
                        (AtomFabric.AtomInstantiationPreventor,),
                        {})

if __name__ == "__main__":
    import doctest
    doctest.testmod()
