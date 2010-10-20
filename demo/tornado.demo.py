#!/usr/bin/python
# -*- coding: utf-8 -*-

import envir # to add upper directory into sys.path, not required for real app

import sys
from agatsuma.web.tornado import TornadoStandaloneCore

# Very important: app root path should also be namespace name
# So if we replace all '/' with '.' in appRoot we should get importable namespace
appRoot = 'demo-tornado'
appConfig = "settings.json"

core = TornadoStandaloneCore([appRoot], appConfig,
            app_name = "TornadoDemoApp",
            #application_spells = ["namespace.module"], # namespaces to load as spells
            #forbidden_spells = ["spellspace.py", "demoapp.demo.multiprocessing_handlers"] # file names or namespaces
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
    entry_pointName = sys.argv[1]
    core.run_entry_point(entry_pointName, sys.argv)

# TODO: session backends: database
# TODO: settings backends: database

# TODO: handlers and formatters configuration for Agatsuma's and named logs
# TODO: webhelpers for tornado apps (?, it's easy to implement without special code inside Agatsuma)

# TODO: Unit tests
# TODO: Sphinx documentation

# TODO: cache services

# TODO: update options via HTTP from master server (or propagate to set of slaves, or re-read from storage)

# ========================== Far far in future =================================
# TODO: tornado: customized errors handling (Tornado patching needed), email reports
# TODO: tornado: more powerful url builder
# TODO: tornado: another template engine (?)
# TODO: tornado: forking support (when new Tornado will be released)

# TODO: type conversion for settings (unicode->str), convert read-only lists to tuples
# TODO: py3k (when dependencies will be ported)
# TODO: debug MW problems in pylons: the only solution is setting debug to false when running pylons under tornado...
