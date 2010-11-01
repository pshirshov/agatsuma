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
"""

class AtomFabric(type):
    class AtomImplementation(type):
        def __eq__(self, other):
            if type(other) == AtomFabric.AtomImplementation:
                return self.__name__ == other.__name__
            return type.__eq__(self, other)

        def __repr__(self):
            return "<atom %s>" % self.__name__

        def __str__(self):
            return self.__name__

    def __getattribute__(stype, name):
        return type.__new__(AtomFabric.AtomImplementation, name, (type,), {})

class Atom(object):
    __metaclass__ = AtomFabric

if __name__ == "__main__":
    import doctest
    doctest.testmod()
