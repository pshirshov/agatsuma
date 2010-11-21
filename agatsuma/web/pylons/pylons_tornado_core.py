# -*- coding: utf-8 -*-

from agatsuma.web.pylons import PylonsAdaptor
from agatsuma.web.tornado import TornadoWSGICore

class PylonsTornadoCore(TornadoWSGICore, PylonsAdaptor):
    """
    """

    def __init__(self, app_directory, appConfig, **kwargs):
        """
        """
        spell_directories = []
        nsFragments = ('agatsuma', 'web', 'pylons', 'spells')

        spell_directories.extend ([self.internal_spell_space(*(nsFragments + ('common', ))),
                            self.internal_spell_space(*(nsFragments + ('tornado', )))
                           ])
        spell_directories.extend(kwargs.get('spell_directories', []))
        kwargs['spell_directories'] = spell_directories

        TornadoWSGICore.__init__(self, app_directory, appConfig, **kwargs)

    def setup_pylons(self, **kwargs):
        PylonsAdaptor.__init__(self, **kwargs)
        self.set_wsgi(self.app)
