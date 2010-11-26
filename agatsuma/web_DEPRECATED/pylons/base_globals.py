# -*- coding: utf-8 -*-

from agatsuma.core import Core
if Core.internal_state.get("mode", None) == "normal":
    from beaker.cache import CacheManager
    from beaker.util import parse_cache_config_options

class BaseGlobals(object):
    """Globals acts as a container for objects available throughout the
    life of the application

    """

    def __init__(self, config):
        """One instance of Globals is created during application
        initialization and is available during requests via the
        'app_globals' variable

        """
        self.cache = CacheManager(**parse_cache_config_options(config))
