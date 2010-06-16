# -*- coding: utf-8 -*-

class PoolEventSpell(object):
    """
    Implementations of this interface may react on process pool events
    (pre- and post-initializaton for now)
    """
    
    def prePoolInit(self, core):
        pass
    
    def postPoolInit(self, core):
        pass
