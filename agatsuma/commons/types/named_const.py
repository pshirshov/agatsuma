#!/bin/env python

"""
This module emulates named constants conception.

>>> from atom import Atom
>>> Atom.const1 == to_atom("const1")
True
>>> test_consts = {Atom.const1 : 123, Atom.test : "test_const"}
>>> proxy = RODictProxy(test_consts)
>>> proxy.const1
123
>>> proxy.non_existent
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
AttributeError: 'RODictProxy' object has no attribute 'non_existent'
>>> proxy.const1 = 456
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
CantOverwriteConstant


>>> Const.register_constants(Atom.set1, test_consts)
>>> Const.set1.const1
123
>>> Const.set1.test
'test_const'
>>> Const.set1 = None
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
CantOverwriteConstantGroup
>>> Const.set2
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
AttributeError: type object 'Const' has no attribute 'set2'
>>> Const.set1.test = 456
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
CantOverwriteConstant
>>> Const.register_constants(Atom.set2, {"non-atomic-key" : 123, Atom.test : 456})
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
AssertionError
"""

from atom import to_atom, is_atom

class RODictProxy(object):
    def __init__(self, source_dict):
        object.__setattr__(self, '_RODictProxy__dict', source_dict)

    def __getattr__(self, name):
        storedDict = object.__getattribute__(self, '_RODictProxy__dict')
        atomic_name = to_atom(name)
        if atomic_name in storedDict:
            return storedDict[atomic_name]
        else:
            return object.__getattribute__(self, name)

    class CantOverwriteConstant(Exception):
        pass
    
    def __setattr__(self, name, value):
        atomic_name = to_atom(name)
        if atomic_name in self.__dict:
            raise RODictProxy.CantOverwriteConstant()
        else:
            object.__setattr__(self, name, value)

class ConstMeta(type):
    class CantOverwriteConstantGroup(Exception):
        pass
    
    def __setattr__(stype, name, value):
       if name in type.__getattribute__(stype, "constant_storage"):
           raise ConstMeta.CantOverwriteConstantGroup()
       else:
           type.__setattr__(stype, name, value)

    def __getattribute__(stype, name):
        storage = type.__getattribute__(stype, "constant_storage")
        if name in storage:
            return storage[name]
        else:
            return type.__getattribute__(stype, name)

class Const(object):
    __metaclass__ = ConstMeta
    constant_storage = {}

    class ConstGroupAlreadyRegistered(Exception):
        pass
    
    @staticmethod
    def register_constants(name, constants):
        assert is_atom(name)
        assert isinstance(constants, dict)

        non_atomic_keys = filter(lambda x: not is_atom(x), constants.keys())
        assert len(non_atomic_keys) == 0
        
        if name in Const.constant_storage:
            raise Const.ConstGroupAlreadyRegistered()
        
        Const.constant_storage[str(name)] = RODictProxy(constants)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
