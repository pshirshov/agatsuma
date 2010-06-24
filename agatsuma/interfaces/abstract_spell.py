# -*- coding: utf-8 -*-

class AbstractSpell(object):
    """ Base class for all the spells. It have some important methods
and callbacks. When Core traversing directories it looks for
implementations of this interface and threats them as spells.

:param spellId: unique identifier (name) of this spell.
    Should match the ``\w+`` regex.

:param spellConfig: dict with optional spell parameters.

The following spell parameters are supported now:

    #. `info` : any string containing readable description for
       this spell
    #. `deps` : tuple of strings which are identifiers of spells
       required for this spell to work (*dependencies*)
    #. `provides` : tuple of strings that describes *functionality*
       provided by this spell (*webPageRender* or *DatabaseDriver*
       for example)
    #. `requires` : tuple of strings that describes which
       functionality required for this spell to work.
    #. `eager_unload` : boolean parameter. When it's set to ``True``
       core unregisters spell recently after completing
       :meth:`agatsuma.interfaces.AbstractSpell.postConfigure` calls.
       This may usable for spells which only required for perform some
       application initialization, such as settings registering
       and data preparation. Also it may be suitable for
       :ref:`dependencies helpers<dependencies-helpers>`.
    """
    
    def __init__(self, spellId, spellConfig = {}):
        self.__pId = spellId
        self.config = spellConfig

        # spell config
        if spellConfig:
            self.__pName = spellConfig.get('info', None)
            self.__pdeps = list(spellConfig.get('deps', () ))

            self.__pProvides = spellConfig.get('provides', () )
            for requirement in spellConfig.get('requires', () ):
                self.__pdeps.append('[%s]' % requirement)
            self.__pdeps = tuple(self.__pdeps)

        # internal variables, init in app_globals.py
        self._setDetails(None, '', '')

    def _setDetails(self, namespace, namespaceName, fileName):
        """ *For internal usage only* """
        self.pnamespace = namespace
        self.pnamespaceName = namespaceName
        self.pfileName = fileName

    def _removeDep(self, dep):
        """ Removes dependency ID from dependency tuple. *For internal usage only* """
        if dep in self.__pdeps:
            deps = list(self.__pdeps)
            deps.remove(dep)
            self.__pdeps = tuple(deps)

    def spellId(self):
        """ Returns name of this spell
        (see `spellConfig` constructor parameter) """
        return self.__pId

    def deps(self):
        """ Returns tuple consists of names of spells required for this spell
        to work (see `spellConfig` constructor parameter).
        """
        return self.__pdeps

    def provides(self):
        """ Returns tuple consists of names of functionality that spell provides
        (see `spellConfig` constructor parameter).
        """
        return self.__pProvides

    def fileName(self):
        """ Returns file name for file containing this spell """
        return self.pfileName

    def namespaceName(self):
        """ Returns namespace name (eg. myapp.foo.bar) for namespace
        containing this spell.
        """
        return self.pnamespaceName

    def namespace(self):
        """ Returns namespace (not the namespace name but namespace itself!)
        containing this spell.
        """
        return self.pnamespace

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

**Solution 3** use of the :attr:`agatsuma.core.Core.internalState`.

``foo.py``::

   from agatsuma.core import Core
   if Core.internalState.get('mode', None) == 'normal':
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
    
    def preConfigure(self, core):
        """ Core calls this method before settings settings service
        initialization. All the options that are needed for spell
        to work should be registered in this method using core method
        :meth:`agatsuma.core.Core.registerOption`

        *Should be overriden in subclasses*
        """
        pass

    def postConfigure(self, core):
        """ Core calls this method subsequent to settings initialization.
        This method intended to preconfigure application related to loaded
        settings (run some threads or open database connections for example)

        *Should be overriden in subclasses*
        """
        pass

    def postConfigUpdate(self, **kwargs):
        """ Settings service calls this method when any writable setting is
        updated. This method may be used to send updated data to worker
        processes for example.

        *Should be overriden in subclasses*
        """
        pass

