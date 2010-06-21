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

