# -*- coding: utf-8 -*-

from agatsuma.log import log
from agatsuma.interfaces import AbstractSpell, IInternalSpell
from agatsuma.web.tornado.interfaces import ISessionBackendSpell
from agatsuma.web.tornado import BaseSessionManager

from agatsuma.elements import Atom

class DummySessionManager(BaseSessionManager):
    def __init__(self):
        BaseSessionManager.__init__(self)
        self.sessions = {}

    def cleanup(self):
        log.sessions.critical("Cleaning not supported, destroying all")
        self.sessions = {}

    def destroy_data(self, sessionId):
        del self.sessions[sessionId]

    def load_data(self, sessionId):
        return self.sessions.get(sessionId, None)

    def save_data(self, sessionId, data):
        self.sessions[sessionId] = data

class DummySessionSpell(AbstractSpell, IInternalSpell, ISessionBackendSpell):
    def __init__(self):
        config = {'info' : 'Dict-based debug session storage',
                  'deps' : (),
                  'provides' : (Atom.session_backend, )
                 }
        AbstractSpell.__init__(self, Atom.tornado_session_backend_dummy, config)

    def instantiate_backend(self, uri):
        log.sessions.critical("Instantiating dummy session backend. URI '%s' ignored" % uri)
        return DummySessionManager()
