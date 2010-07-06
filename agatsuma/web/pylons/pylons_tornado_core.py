# -*- coding: utf-8 -*-

from agatsuma.web.pylons import PylonsAdaptor
from agatsuma.web.tornado import TornadoWSGICore

class PylonsTornadoCore(TornadoWSGICore, PylonsAdaptor):
    """
    """

    def __init__(self, appDir, appConfig, **kwargs):
        """
        """
        TornadoWSGICore.__init__(self, appDir, appConfig, **kwargs)
        PylonsAdaptor.__init__(self, **kwargs)
        self.setWSGI(self.app)
