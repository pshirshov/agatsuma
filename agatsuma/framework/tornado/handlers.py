# -*- coding: utf-8 -*-

import tornado.web
import logging
from agatsuma.core import Core
from agatsuma.interfaces import RequestSpell
from agatsuma.errors import EAbstractFunctionCall

class AgatsumaHandler(tornado.web.RequestHandler):
    def __init__(self, application, request, transforms=None):
        tornado.web.RequestHandler.__init__(self, application, request, transforms)

    def prepare(self):
        spells = self.application._implementationsOf(RequestSpell)
        for spell in spells:
            spell.beforeRequestCallback(self)
        
    def async(self, method, args, callback):
        self.application.pool.apply_async(method, 
                                          (id(self), ) + args, 
                                          callback=self.async_callback(callback)) 
        
class MsgPumpHandler(AgatsumaHandler):
    def __init__(self, application, request):
        AgatsumaHandler.__init__(self, application, request)
        application.handlerInitiated(self)
        
    @staticmethod
    def sendMessage(id, message):
        Core.mqueue.put((id, message))
        
    def processMessage(self, message):
        raise EAbstractFunctionCall() 
        
    def waitForQueue(self, callback):
        self.application.waitingCallbacks.append(callback)