# -*- coding: utf-8 -*-

class ISetupSpell(object):
    """
    """
    def requirements(self):
        """This method should return dict with string keys
and lists of strings as values.

Dict values describes describe spell dependencies
setuptools format (like ``['libfoo>=0.1.2', 'libbar=1.2']``)
Dict keys are responsible to dependencies groups that
may be used to install only the required dependencies.

When you call *setup.py* all the requirements from
all the available spells will be added to dependencies list.

So if spell can't be imported due to non-existent dependencies
(``import libfoo`` for non-existent ``libfoo`` in spell's file)
it will be not loaded and it's dependencies will be not
added to dependencies list.

It may be good idea to place spell with requirements into
separate file without dangerous imports.

But here is a big problem: if module containing spell
does imports that may not be installed on target system
when core will fail at importing stage and will not
load spell. You have at least 3 slightly different solutions for this
problem.

.. _dependencies-helpers:

Assume you've written file ``foo.py`` with the following
content::

   import SomeBigLibrary

   from agatsuma.interfaces import AbstractSpell

   class MySpell(AbstractSpell):
       def __init__(self):
           config = {'info' : 'My Spell',
                     }
           AbstractSpell.__init__(self, 'my_spell', config)

       def requirements(self):
               return {'importantlibs' : []'SomeBigLibrary>=1.2.3'],
                       }

       def something(self):
           SomeBigLibrary.makeAllGood()


**Solution 1** split ``foo.py`` into two files (``foo.py`` and
``foo_deps.py`` for example):

``foo.py``::

   import SomeBigLibrary

   from agatsuma.interfaces import AbstractSpell

   class MySpell(AbstractSpell):
       def __init__(self):
           config = {'info' : 'My Spell',
                     }
           AbstractSpell.__init__(self, 'my_spell', config)

       def something(self):
           SomeBigLibrary.makeAllGood()

``foo_deps.py``::

   from agatsuma.interfaces import AbstractSpell

   class MySpellDependenciesHelper(AbstractSpell):
       def __init__(self):
           config = {'info' : 'My Spell dependencies helper',
                     'eager_unload' : True,
                     }
           AbstractSpell.__init__(self, 'my_spell_dephelper', config)

       def requirements(self):
           return {'importantlibs' : ['SomeBigLibrary>=1.2.3'],
                  }

**Solution 2** avoid of using global imports:

``foo.py``::

   from agatsuma.interfaces import AbstractSpell

   class MySpell(AbstractSpell):
       def __init__(self):
           config = {'info' : 'My Spell',
                     }
           AbstractSpell.__init__(self, 'my_spell', config)

       def requirements(self):
               return {'importantlibs' : ['SomeBigLibrary>=1.2.3'],
                       }

       def something(self):
           import SomeBigLibrary
           SomeBigLibrary.makeAllGood()

**Solution 3** use of the :attr:`agatsuma.core.Core.internal_state`.

``foo.py``::

   from agatsuma.core import Core
   if Core.internal_state.get('mode', None) == 'normal':
       import SomeBigLibrary

   from agatsuma.interfaces import AbstractSpell

   class MySpell(AbstractSpell):
       def __init__(self):
           config = {'info' : 'My Spell',
                     }
           AbstractSpell.__init__(self, 'my_spell', config)

       def requirements(self):
               return {'importantlibs' : ['SomeBigLibrary>=1.2.3'],
                       }

       def something(self):
           SomeBigLibrary.makeAllGood()

        """
        return {}

    def py_entry_points(self):
        """
        {'section' : [('name', 'namespace', 'entrypoint'), ],
        }
        """
        return {}
