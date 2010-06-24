# -*- coding: utf-8 -*-

from agatsuma.log import log
from agatsuma.interfaces import AbstractSpell
from agatsuma.framework.tornado.interfaces import SessionBackendSpell
from agatsuma.framework.tornado import BaseSessionManager

class DummySessionManager(BaseSessionManager):
    def __init__(self):
        BaseSessionManager.__init__(self)
        self.sessions = {}     

    def cleanup(self):
        log.sessions.critical("Cleaning not supported, destroying all")
        self.sessions = {}

    def destroyData(self, sessionId):
        del self.sessions[sessionId]

    def loadData(self, sessionId):
        return self.sessions.get(sessionId, None)

    def saveData(self, sessionId, data):
        self.sessions[sessionId] = data

class DummySessionSpell(AbstractSpell, SessionBackendSpell):
    def __init__(self):
        config = {'info' : 'Dict-based debug session storage',
                  'deps' : (),
                  'provides' : ('session_backend', )
                 }
        AbstractSpell.__init__(self, 'tornado_session_backend_dummy', config)
        
    def instantiateBackend(self, uri):
        log.sessions.critical("Instantiating dummy session backend. URI '%s' ignored" % uri)
        return DummySessionManager()
