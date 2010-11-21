# -*- coding: utf-8 -*-

class AbstractSpell(object):
    """ Base class for all the spells. It have some important methods
and callbacks. When Core traversing directories it looks for
implementations of this interface and threats them as spells.

:param spell_id: unique identifier (name) of this spell.
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
       :meth:`agatsuma.interfaces.AbstractSpell.post_configure` calls.
       This may usable for spells which only required for perform some
       application initialization, such as settings registering
       and data preparation. Also it may be suitable for
       :ref:`dependencies helpers<dependencies-helpers>`.
    """

    def __init__(self, spell_id, spellConfig = {}):
        self.__pId = spell_id
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
        self._set_details(None, '', '')

    def _set_details(self, namespace, namespace_name, file_name):
        """ *For internal usage only* """
        self.pnamespace = namespace
        self.pnamespace_name = namespace_name
        self.pfile_name = file_name

    def _remove_dep(self, dep):
        """ Removes dependency ID from dependency tuple. *For internal usage only* """
        if dep in self.__pdeps:
            deps = list(self.__pdeps)
            deps.remove(dep)
            self.__pdeps = tuple(deps)

    def spell_id(self):
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

    def file_name(self):
        """ Returns file name for file containing this spell """
        return self.pfile_name

    def namespace_name(self):
        """ Returns namespace name (eg. myapp.foo.bar) for namespace
        containing this spell.
        """
        return self.pnamespace_name

    def namespace(self):
        """ Returns namespace (not the namespace name but namespace itself!)
        containing this spell.
        """
        return self.pnamespace

    def pre_configure(self, core):
        """ Core calls this method before settings settings service
        initialization. All the options that are needed for spell
        to work should be registered in this method using core method
        :meth:`agatsuma.core.Core.register_option`

        *Should be overriden in subclasses*
        """
        pass

    def post_configure(self, core):
        """ Core calls this method subsequent to settings initialization.
        This method intended to preconfigure application related to loaded
        settings (run some threads or open database connections for example)

        *Should be overriden in subclasses*
        """
        pass

    def post_config_update(self, **kwargs):
        """ Settings service calls this method when any writable setting is
        updated. This method may be used to send updated data to worker
        processes for example.

        *Should be overriden in subclasses*
        """
        pass
