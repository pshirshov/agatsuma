# -*- coding: utf-8 -*-

from agatsuma.web.pylons import PylonsAdaptor
from agatsuma.web.tornado import TornadoWSGICore

class PylonsTornadoCore(TornadoWSGICore, PylonsAdaptor):
    """
    """

    def __init__(self, appDir, appConfig, **kwargs):
        """
        """
        spellsDirs = []
        nsFragments = ('agatsuma', 'web', 'pylons', 'spells')

        spellsDirs.extend ([self._internalSpellSpace(*(nsFragments + ('common', ))),
                            self._internalSpellSpace(*(nsFragments + ('tornado', )))
                           ])
        spellsDirs.extend(kwargs.get('spellsDirs', []))
        kwargs['spellsDirs'] = spellsDirs

        TornadoWSGICore.__init__(self, appDir, appConfig, **kwargs)

    def setupPylons(self, **kwargs):
        PylonsAdaptor.__init__(self, **kwargs)
        self.setWSGI(self.app)
