# -*- coding: utf-8 -*-

import tornado.web
import logging
from agatsuma.core import Core

class FidelityWorker(object):
    functions = {}
    def __init__(self, worker):
        self.workerId = id(worker)
        self.workerName = worker.__name__
        FidelityWorker.functions[self.workerId] = worker

    def __call__(self, *args, **kwargs):
        try:
            return FidelityWorker.functions[self.workerId](*args, **kwargs)
        except Exception, e:
            logging.error("Exception in MP worker", exc_info=True)

class AgatsumaHandler(tornado.web.RequestHandler):
    def async(self, method, args, callback):
        self.application.pool.apply_async(method, 
                                          (id(self), ) + args, 
                                          callback=self.async_callback(callback)) 
      
class EAbstractFunctionCall(Exception):
    def __repr__(self):
        return "Call to abstract function"
        
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