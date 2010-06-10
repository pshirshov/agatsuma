# -*- coding: utf-8 -*-

import os

from agatsuma.log import log
from agatsuma.settings import Settings
from agatsuma.session.base_session import Session

class BaseSessionManager(object):
    def __init__(self):
        # TODO: get settings and open connection in children
        pass

    def _generate_session_id(cls):
        return os.urandom(32).encode('hex') # 256 bits of entropy    

    def new(self):
        pass

    def load(self, sessionId):
        """Load the stored session from storage backend or return
           None if the session was not found, in case of stale cookie."""
        pass

    def cleanup(self):
        """Deletes sessions with timestamps in the past form storage."""
        pass
    
    def save(self, session):
        pass

    def delete(self, session):
        pass

    def destroyData(self, sessionId):
        pass

    def loadData(self, sessionId):
        pass

import datetime
import copy

class DummySessionManager(BaseSessionManager):
    def __init__(self):
        self.sessions = {}
       
    def new(self, ip, user_agent):
        newId = self._generate_session_id()
        #sess = Session(newId, { 'timestamp' : datetime.datetime.now() }) #, self, None)
        sess = Session(newId, {})
        sess.fill(ip, user_agent)
        return sess

    def sessionDoomsday(self, moment):
        return moment + datetime.timedelta(seconds=Settings.sessions.expiration_interval)

    def load(self, sessionId):
        sessData = self.loadData(sessionId)
        print "LOADED>", sessData
        if sessData:
            if datetime.datetime.now() >= self.sessionDoomsday(sessData["timestamp"]):
                self.destroyData(sessionId)
                print "destroying session"
                return None
            sess = Session(sessionId, sessData) #, self, None)    
            sess.saved = True
            return sess
 
    def cleanup(self):
        print "NOT IMPLEMENTED"
        """
        for sessId in self.sessions:
            sessData = self.sessions[sessId]
            if sessData["expirationTime"] < datetime.datetime.now():
                del self.sessions[sessId]
        """
        
    def save(self, session):
        print "SAVE>", session.data
        session["timestamp"] = datetime.datetime.now()
        self.saveData(session.id, session.data)
        if session.handler and not session.cookieSent:
            print "setting cookie"
            session.handler.set_secure_cookie(u"AgatsumaSessId", session.id)
            session.cookieSent = True
        else:
            print "session saved without cookie setting"
        session.saved = True
        
    def delete(self, session):
        if session.id in self.sessions:
            self.destroyData(session.id)
            if session.handler:
                session.handler.clear_cookie("AgatsumaSessId")
            else:
                print "session removed without cookie setting"
        else:
            print "deleting deleted"
        session.saved = False

    def destroyData(self, sessionId):
        del self.sessions[sessionId]

    def loadData(self, sessionId):
        return self.sessions.get(sessionId, None)

    def saveData(self, sessionId, data):
        self.sessions[sessionId] = data

