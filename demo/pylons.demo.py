#!/usr/bin/env python
# -*- coding: utf-8 -*-

import envir # to add upper directory into sys.path, not required for real app

#import helloworld.lib.app_globals as app_globals
#import helloworld.lib.helpers
#from helloworld.config.routing import make_map

appRoot = 'demo_pylons'
appConfig = "settings.pylons.json"

from agatsuma.web.pylons import BaseGlobals, PylonsTornadoCore


class AppGlobals(BaseGlobals):
    def __init__(self, config):
        BaseGlobals.__init__(self, config)

glob = {'debug': 'false', 'error_email_from': 'paste@localhost', '__file__': '/home/user/work/helloworld/development.ini',
        'here': '/home/user/work/trustimex', 'smtp_server': 'localhost'}

app = {'beaker.session.key': 'helloworld',
       'cache_dir': '/home/user/work/helloworld/data',
       'beaker.session.secret': 'somesecret'}


from demo_pylons.lib import helpers
core = PylonsTornadoCore([appRoot], appConfig, helpers = helpers,
                         globals_class = AppGlobals,
                         pylons_root = appRoot,
                         global_conf = glob,
                         app_conf = app,
                        full_stack=True, static_files=True, )
core.start()
