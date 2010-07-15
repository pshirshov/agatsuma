#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("../../") # only for demo app

appRoot = 'demo_pylons'
appConfig = "settings.pylons.json"

from agatsuma import Settings
from agatsuma.web.pylons import BaseGlobals, PylonsTornadoCore

class AppGlobals(BaseGlobals):
    def __init__(self, config):
        BaseGlobals.__init__(self, config)

from demo_pylons.lib import helpers
core = PylonsTornadoCore([appRoot], appConfig)
core.setupPylons(helpers = helpers,
                 globals_class = AppGlobals,
                 pylons_root = appRoot,
                 global_conf = Settings.pylons.glob,
                 app_conf = Settings.pylons.app,
                 full_stack=Settings.pylons.full_stack,
                 static_files=Settings.pylons.static_files,
                 )
core.start()
