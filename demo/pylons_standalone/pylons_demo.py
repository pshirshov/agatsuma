#!/usr/bin/env python
# -*- coding: utf-8 -*-

appRoot = 'pylons_standalone'
appConfig = "settings.pylons.json"

import sys

sys.path.append("../../") # only for demo app
print sys.path
from agatsuma.web.pylons import BaseGlobals, PylonsCore

class AppGlobals(BaseGlobals):
    def __init__(self, config):
        BaseGlobals.__init__(self, config)

def make_core(*args, **kwargs):
    return PylonsCore([(appRoot, "pylons_standalone")], *args, **kwargs)

# Entry points are provided by spell in appspell.py
# Don't forget to generate egg info before running paster with "./setup.py egg_info"
def make_app(global_conf, full_stack=True, static_files=True, **app_conf):
    from pylons_standalone.lib import helpers
    core = make_core(appConfig, helpers = helpers,
                             globals_class = AppGlobals,
                             pylons_root = appRoot,
                             global_conf = global_conf,
                             app_conf = app_conf,
                             full_stack=full_stack, static_files=static_files,
                     )
    return core.app
