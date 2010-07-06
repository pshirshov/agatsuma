# -*- coding: utf-8 -*-

from agatsuma.core import BaseCore
from agatsuma.web.pylons import PylonsAdaptor

class PylonsCore(BaseCore, PylonsAdaptor):
    def __init__(self, appDir, appConfig, **kwargs):
        """
        """
        spellsDirs = []
        nsFragments = ('agatsuma', 'web', 'pylons', 'spells', 'common')
        spellsDirs.extend ([self._internalSpellSpace(*nsFragments)
                            ])
        spellsDirs.extend(kwargs.get('spellsDirs', []))
        kwargs['spellsDirs'] = spellsDirs

        BaseCore.__init__(self, appDir, appConfig, **kwargs)
        PylonsAdaptor.__init__(self, **kwargs)

