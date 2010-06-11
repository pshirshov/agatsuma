#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from agatsuma.framework.tornado import TornadoCore
from agatsuma.log import log

# Very important: app root path should also be namespace name
# So if we replace all '.' to '/' in appRoot we should get importable namespace
appRoot = 'demoapp' 
appConfig = "settings.json"

core = TornadoCore(appRoot, appConfig, 
            appName = "Agatsuma Demo Application",
            #appSpells = ["namespace.module"], # namespaces to load as spells
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

# TODO: session backends: memcache, database
# TODO: remove SQLA variables from core
# TODO: pool disabling
# TODO: settings checks/fixes

# TODO: url building
# TODO: x-headers
# TODO: settings saving (maybe into database)
# TODO: Unit tests
# TODO: Sphinx documentation

# TODO: template engine
# TODO: caching decorator
# TODO: applyFilters    

# TODO: customized errors handling (Tornado patching needed)
# TODO: py3k (when Tornado will be ported)
# TODO: Tornado forking support (when new Tornado will be released)
# TODO: update options via HTTP from master server (or propagate to set of slaves)
