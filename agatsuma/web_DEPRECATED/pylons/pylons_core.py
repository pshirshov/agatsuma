# -*- coding: utf-8 -*-

from agatsuma.core import Core
from agatsuma.web.pylons import PylonsAdaptor

class PylonsCore(Core, PylonsAdaptor):
    def __init__(self, app_directory, appConfig, **kwargs):
        """
        """
        spell_directories = []
        nsFragments = ('agatsuma', 'web', 'pylons', 'spells', 'common')
        spell_directories.extend ([self.internal_spell_space(*nsFragments)
                            ])
        spell_directories.extend(kwargs.get('spell_directories', []))
        kwargs['spell_directories'] = spell_directories

        Core.__init__(self, app_directory, appConfig, **kwargs)
        PylonsAdaptor.__init__(self, **kwargs)
