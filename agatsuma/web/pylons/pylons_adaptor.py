# -*- coding: utf-8 -*-

import os

from agatsuma.core import Core
if Core.internal_state.get("mode", None) == "normal":
    from pylons.configuration import PylonsConfig
    from pylons.error import handle_mako_error
    from pylons.middleware import ErrorHandler, StatusCodeRedirect
    from pylons.wsgiapp import PylonsApp

    from paste.cascade import Cascade
    from paste.registry import RegistryManager
    from paste.urlparser import StaticURLParser
    from paste.deploy.converters import asbool

    from beaker.middleware import SessionMiddleware

    from routes.middleware import RoutesMiddleware
    from routes import Mapper
    from mako.lookup import TemplateLookup

from agatsuma import Implementations, log
from agatsuma.web.pylons.interfaces import IMiddlewareSpell, IHandlingSpell

class PylonsAdaptor(object):
    """
    """

    def __init__(self, **kwargs):
        """
        """
        if Core.internal_state.get("mode", None) == "normal":
            log.pcore.debug("Initializing Pylons...")
            pylonsRoot = kwargs['pylons_root']
            global_conf = kwargs['global_conf']
            app_conf = kwargs['app_conf']
            #app_name = kwargs['app_name']
            helpers = kwargs['helpers']
            GlobalsClass = kwargs['globals_class']
            config = self._load_environment(pylonsRoot,
                                           global_conf, app_conf,
                                           GlobalsClass, helpers)
            full_stack = kwargs['full_stack']
            static_files = kwargs['static_files']
            self.app = self._make_app(config, full_stack, static_files)
        else:
            log.core.warning("Setup mode. Pylons initialization skipped")
            self.app = None

    def _make_app(self, config, full_stack=True, static_files=True):
        # The Pylons WSGI app
        log.pcore.debug("Initializing middleware...")
        app = PylonsApp(config=config)
        # Routing/Session Middleware
        app = RoutesMiddleware(app, config['routes.map'], singleton=False)
        app = SessionMiddleware(app, config)

        # CUSTOM MIDDLEWARE HERE (filtered by error handling middlewares)
        spells = Implementations(IMiddlewareSpell)
        for spell in spells:
            app = spell.add_middleware(app)

        if asbool(full_stack):
            # Handle Python exceptions
            global_conf = config # I think that it's correct, config is slightly modified global_conf
            app = ErrorHandler(app, global_conf, **config['pylons.errorware'])

            # Display error documents for 401, 403, 404 status codes (and
            # 500 when debug is disabled)
            if asbool(config['debug']):
                app = StatusCodeRedirect(app)
            else:
                app = StatusCodeRedirect(app, [400, 401, 403, 404, 500])

        # Establish the Registry for this application
        app = RegistryManager(app)

        if asbool(static_files):
            # Serve static files
            static_app = StaticURLParser(config['pylons.paths']['static_files'])
            app = Cascade([static_app, app])
            app.config = config
        return app

    def _load_environment(self, pylonsRoot, global_conf, app_conf, GlobalsClass, helpers):
        log.pcore.debug("Loading environment...")
        """Configure the Pylons environment via the ``pylons.config``
        object
        """
        log.pcore.debug("global_conf for Pylons: %s" % str(global_conf))
        log.pcore.debug("app_conf for Pylons: %s" % str(app_conf))

        config = PylonsConfig()

        # Pylons paths
        root = os.path.abspath(pylonsRoot) #os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        paths = dict(root=root,
                     controllers=os.path.join(root, 'controllers'),
                     static_files=os.path.join(root, 'public'),
                     templates=[os.path.join(root, 'templates')])

        # Initialize config with the basic options
        config.init_app(global_conf,
                        app_conf,
                        package=pylonsRoot,
                        paths=paths)

        config['routes.map'] = self._makeMap(config)
        config['pylons.app_globals'] = GlobalsClass(config)
        config['pylons.h'] = helpers

        # Setup cache object as early as possible
        import pylons
        pylons.cache._push_object(config['pylons.app_globals'].cache)

        # Create the Mako TemplateLookup, with the default auto-escaping
        config['pylons.app_globals'].mako_lookup = TemplateLookup(
            directories=paths['templates'],
            error_handler=handle_mako_error,
            module_directory=os.path.join(app_conf['cache_dir'], 'templates'),
            input_encoding='utf-8',
            default_filters=['escape'],
            imports=['from webhelpers.html import escape'])

        # CONFIGURATION OPTIONS HERE (note: all config options will override
        # any Pylons config options)
        # TODO: call spells ???
        return config

    def _makeMap(self, config):
        log.pcore.debug("Setting up routes...")
        """Create, configure and return the routes Mapper"""
        map = Mapper(directory=config['pylons.paths']['controllers'],
                     always_scan=config['debug'])
        map.minimization = False
        map.explicit = False

        # The ErrorController route (handles 404/500 error pages); it should
        # likely stay at the top, ensuring it can always be resolved
        # TODO: ??? Is it really required ???
        map.connect('/error/{action}', controller='error')
        map.connect('/error/{action}/{id}', controller='error')

        # CUSTOM ROUTES HERE
        print IHandlingSpell
        spells = Implementations(IHandlingSpell)
        print ">>>", spells
        for spell in spells:
            spell.init_routes(map)
        for spell in spells:
            spell.post_init_routes(map)

        return map
