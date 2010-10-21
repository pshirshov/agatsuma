# -*- coding: utf-8 -*-

from pylons.controllers import WSGIController
from pylons.templating import render_mako as __render

from agatsuma import Implementations
from agatsuma.web.pylons.interfaces import RequestSpell

class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        spells = Implementations(RequestSpell)
        for spell in spells:
            spell.before_request(self, environ, start_response)
        
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        return WSGIController.__call__(self, environ, start_response)

    def render(self, *args, **kwargs):
        return __render(*args, **kwargs)
