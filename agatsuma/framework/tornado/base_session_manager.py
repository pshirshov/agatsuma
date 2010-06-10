# -*- coding: utf-8 -*-

import datetime
import os

from agatsuma.log import log
from agatsuma.settings import Settings
from agatsuma.interfaces import Session

class BaseSessionManager(object):
    def __init__(self):
        pass

    def _generate_session_id(cls):
        return os.urandom(32).encode('hex')
        
    def _sessionDoomsday(self, moment):
        return moment + datetime.timedelta(seconds=Settings.sessions.expiration_interval)
        
    def new(self, ip, user_agent):
        newId = self._generate_session_id()
        sess = Session(newId, {})
        sess.fill(ip, user_agent)
        return sess
        
    def load(self, sessionId):
        sessData = self.loadData(sessionId)
        log.sessions.debug("Loaded session %s with data %s loaded" % (sessionId, str(sessData)))
        if sessData:
            if datetime.datetime.now() >= self._sessionDoomsday(sessData["timestamp"]):
                log.sessions.debug("Session %s expired and destroyed" % sessionId)
                self.destroyData(sessionId)
                return None
            sess = Session(sessionId, sessData)
            sess.saved = True
            return sess

    def save(self, session):
        session["timestamp"] = datetime.datetime.now()
        self.saveData(session.id, session.data)
        if session.handler and not session.cookieSent:
            log.sessions.debug("Session %s with data %s saved and cookie set" % (session.id, str(session.data)))
            session.handler.set_secure_cookie(u"AgatsumaSessId", session.id)
            session.cookieSent = True
        else:
            log.sessions.debug("Session %s with data %s saved but cookie not set" % (session.id, str(session.data)))
        session.saved = True
        
    def delete(self, session):
        self.destroyData(session.id)
        if session.handler:
            session.handler.clear_cookie("AgatsumaSessId")
        else:
            log.sessions.warning("Session %s with data %s destroyed but cookie not cleared: no handler" % (session.id, str(session.data)))
        session.saved = False

    def cleanup(self):
        """Deletes sessions with timestamps in the past form storage."""
        pass
    
    def destroyData(self, sessionId):
        """ destroys session in storage """
        pass

    def loadData(self, sessionId):
        """ returns session data if exists, otherwise returns None """
        pass



