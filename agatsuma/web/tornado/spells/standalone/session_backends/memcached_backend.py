# -*- coding: utf-8 -*-
import re
import time
import datetime

try:
    import cPickle as pickle
except ImportError:
    import pickle

from agatsuma import log
#from agatsuma.settings import Settings
#from agatsuma import Core
from agatsuma import Spell
from agatsuma.interfaces import AbstractSpell
from agatsuma.web.tornado.interfaces import SessionBackendSpell
from agatsuma.web.tornado import BaseSessionManager

class MemcachedSessionManager(BaseSessionManager):
    def __init__(self, uri):
        BaseSessionManager.__init__(self)
        self.uri = uri
        self.initConnection()

    def initConnection(self):
        log.sessions.info("Initializing Memcached session backend "\
                          "using URI '%s'" % self.uri)
        self.keyprefix = self._parseMemcachedPrefixUri(self.uri)
        memcachedSpell = Spell("agatsuma_memcached")
        self.pool = memcachedSpell.getConnectionPool()

    @property
    def connection(self):
        with self.pool.reserve() as mc:
            return mc

    def _getPrefixedKey(self, sessionId):
        if self.keyprefix:
            return str("%s_%s" % (self.keyprefix, sessionId))
        return sessionId

    @staticmethod
    def _parseMemcachedPrefixUri(details):
        # memprefix://prefixname
        match = re.match('^memprefix://(\w+)$', details)
        return match.group(1) if match else ''

    def cleanup(self):
        """With Memcached as session storage, this function does
        not make sense as all keys are saved with expiry time
        exactly the same as the session's. Hence Memcached takse
        care of cleaning out the garbage."""
        pass

    def destroyData(self, sessionId):
        if not self.connection.remove(self._getPrefixedKey(sessionId)):
            log.sessions.info("Deleting seesion %s failed. It was probably "\
                              "not set or expired" % sessionId)

    def loadData(self, sessionId):
        data = self.connection.get(self._getPrefixedKey(sessionId))
        if data:
            return pickle.loads(data)

    def saveData(self, sessionId, data):
        expTime = int(time.mktime(
          self._sessionDoomsday(datetime.datetime.now()).timetuple()))
        if not self.connection.set(self._getPrefixedKey(sessionId),
                                   pickle.dumps(data), time=expTime):
            log.sessions.critical("Saving %s session failed" % sessionId)

class MemcachedSessionSpell(AbstractSpell, SessionBackendSpell):
    def __init__(self):
        config = {'info' : 'Memcached session storage',
                  'deps' : ('agatsuma_memcached', ),
                  'provides' : ('session_backend', )
                 }
        AbstractSpell.__init__(self, 'tornado_session_backend_memcached',
                               config)

    def instantiateBackend(self, uri):
        self.managerInstance = MemcachedSessionManager(uri)
        return self.managerInstance
