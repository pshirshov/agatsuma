# -*- coding: utf-8 -*-

from agatsuma.core import Core
if Core.internal_state.get("mode", None) == "normal":
    import pylons.controllers
    WSGIController = pylons.controllers.WSGIController
    from pylons.templating import render_mako as __render
else:
    WSGIController = object

from agatsuma import Implementations
from agatsuma.web.pylons.interfaces import IRequestSpell

class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        spells = Implementations(IRequestSpell)
        for spell in spells:
            spell.before_request(self, environ, start_response)

        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        return WSGIController.__call__(self, environ, start_response)

    def render(self, *args, **kwargs):
        return __render(*args, **kwargs)
