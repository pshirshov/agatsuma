# -*- coding: utf-8 -*-

class IFilteringSpell(object):
    """ This mix-in interface is intended to provide functions that
    performs substring replacements.

    All such functions are chained and you can use core method
    **TODO** to call them. This may be suitable, for example, to
    implement word-filter on website.
    """
    def __init__(self):
        pass
    
    def filters_ist(self):
        """ This method should return list or tuple of functions
        that have one string argument and returns string
        """
        return []
        
    #TODO: templating and this
    """
    def global_filters_list(self):
        return []
    """
