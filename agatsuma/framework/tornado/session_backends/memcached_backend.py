# -*- coding: utf-8 -*-
import re
import time
import datetime

try:
    import cPickle as pickle
except ImportError:
    import pickle

from agatsuma.log import log
from agatsuma.settings import Settings
from agatsuma.core import Core
from agatsuma.interfaces import AbstractSpell
from agatsuma.framework.tornado import SessionBackendSpell
from agatsuma.framework.tornado import BaseSessionManager

class MemcachedSessionManager(BaseSessionManager):
    def __init__(self, uri):
        BaseSessionManager.__init__(self)
        self.uri = uri
        self.initConnection()

    def initConnection(self):
        log.sessions.info("Initializing Memcached session backend "\
                          "using URI '%s'" % self.uri)
        self.keyprefix = self._parseMemcachedPrefixUri(self.uri)
        memcachedSpell = Core.instance.spellsDict["agatsuma_memcached"]
        self.connection = memcachedSpell.connection

    def _getPrefixedKey(key):
        if self.key:
            return "%s_%s" % (self.key, session_id)
        return session_id

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

    def destroyData(self, session_id):
        if not self.connection.remove(self._getPrefixedKey(session_id)):
            log.sessions.info("Deleting seesion %s failed. It was probably "\
                              "not set or expired" % session_id)

    def loadData(self, session_id):
        data = self.connection.get(self._getPrefixedKey(session_id))
        if data:
            return pickle.loads(data)

    def saveData(self, session_id, data):
        expTime = int(time.mktime(
          self._sessionDoomsday(datetime.datetime.now()).timetuple()))
        if not self.connection.set(self._getPrefixedKey(session_id),
                                   pickle.dumps(data), time=expTime):
            log.sessions.critical("Saving %s session failed" % session_id)

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
