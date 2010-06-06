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
except (KeyboardInterrupt, SystemExit):
    core.stop()

# TODO: tornado-independent core
# TODO: entry points analogue
# TODO: deployment
# TODO: py3k
# TODO: sessions
# TODO: url building
# TODO: customized URL handling

# TODO: template engine
# TODO: caching decorator
# TODO: applyFilters    

# TODO: Tornado forking support (when new Tornado will be released)
# TODO: update options via HTTP from master server (or propagate to set of slaves)
