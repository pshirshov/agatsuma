#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from agatsuma.core import Core
from agatsuma.log import log

appRoot = os.path.join(os.path.dirname(__file__), 'demoapp')
appRoot = os.path.realpath(appRoot)
appConfig = "settings.json"
core = Core(appRoot, appConfig, 
            appName = "Agatsuma Demo Application",
            appSpells = ["core_spell", "core_filters", "core_sqla"])
try:
    core.start()
except Exception, e:
    print e
finally:    
    log.core.info("Stopping server...")
    #core.stop()

# TODO: template engine
# TODO: deployment
# TODO: caching decorator
# TODO: alchemy
# TODO: applyFilters    
# TODO: py3k
# TODO: entry points analogue
# TODO: update options via HTTP from master server (or propagate to set of slaves)