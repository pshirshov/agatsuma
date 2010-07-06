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
            appName = "TornadoDemoApp",
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

# TODO: session backends: database
# TODO: settings backends: database

# TODO: handlers' configuration
# TODO: pylons spells
# TODO: paster compatibility for pylons standalone mode
# TODO: debug MW problems in pylons
# TODO: webhelpers

# TODO: Unit tests
# TODO: Sphinx documentation

# TODO: cache services

# TODO: type conversion for settings (unicode->str), convert read-only lists to tuples
# TODO: update options via HTTP from master server (or propagate to set of slaves, or re-read from storage)
# TODO: multiple sessions backends
# TODO: list of session backends instead of one

# TODO: tornado: customized errors handling (Tornado patching needed), email reports
# TODO: tornado: more powerful url builder
# TODO: tornado: another template engine (?)
# TODO: tornado: forking support (when new Tornado will be released)

# TODO: py3k (when dependencies will be ported)
