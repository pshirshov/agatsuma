# -*- coding: utf-8 -*-

from pylons.controllers import WSGIController
from pylons.templating import render_mako as __render

class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        return WSGIController.__call__(self, environ, start_response)

    def render(self, *args, **kwargs):
        return __render(*args, **kwargs)
