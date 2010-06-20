# -*- coding: utf-8 -*-

class AbstractSpell(object):
    def __init__(self, spellId, spellConfig = False):
        self.__pId = spellId

        # spell config
        if spellConfig:
            self.config = spellConfig

            self.__pName = spellConfig.get('info', None)
            self.__pdeps = list(spellConfig.get('deps', () ))

            self.__pProvides = spellConfig.get('provides', () )
            for requirement in spellConfig.get('requires', () ):
                self.__pdeps.append('[%s]' % requirement)
            self.__pdeps = tuple(self.__pdeps)

        # internal variables, init in app_globals.py
        self.setDetails(None, '', '')

    def setDetails(self, namespace, namespaceName, fileName):
        self.pnamespace = namespace
        self.pnamespaceName = namespaceName
        self.pfileName = fileName

    def spellId(self):
        return self.__pId

    def fileName(self):
        return self.pfileName

    def namespaceName(self):
        return self.pnamespaceName

    def namespace(self):
        return self.pnamespace

    def deps(self):
        return self.__pdeps

    def _removeDep(self, dep):
        if dep in self.__pdeps:
            deps = list(self.__pdeps)
            deps.remove(dep)
            self.__pdeps = tuple(deps)
        
    def provides(self):
        return self.__pProvides

    def preConfigure(self, core):
        pass

    def postConfigure(self, core):
        pass

    def postConfigUpdate(self, **kwargs):
        pass

