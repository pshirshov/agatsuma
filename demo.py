#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from agatsuma.core import Core
from agatsuma.log import log

appRoot = os.path.join(os.path.dirname(__file__), 'demoapp')
appRoot = os.path.realpath(appRoot)
appConfig = "settings.json"

print sys.argv

core = Core(appRoot, appConfig, 
            appName = "Agatsuma Demo Application",
            appSpells = ["core_spell", "core_filters", "core_sqla"],
            #prohibitedSpells = ["spellspace.py", "demoapp.demo.multiprocessing_handlers"] # file names or namespaces
            )

"""
To drop all tables and init database run:
    ./demo.py agatsuma:sqla_init recreate
To init database without dropping tables run:
    ./demo.py agatsuma:sqla_init
To test entry points run:
    ./demo.py demoPoint
"""
if len(sys.argv) < 2:            
    try:
        core.start()
    except (KeyboardInterrupt, SystemExit):
        core.stop()
else:
    entryPointName = sys.argv[1]
    core.runEntryPoint(entryPointName, sys.argv)

# TODO: tornado-independent core
# TODO: py3k
# TODO: sessions
# TODO: url building
# TODO: customized errors handling
# TODO: x-headers

# TODO: template engine
# TODO: caching decorator
# TODO: applyFilters    

# TODO: Tornado forking support (when new Tornado will be released)
# TODO: update options via HTTP from master server (or propagate to set of slaves)
