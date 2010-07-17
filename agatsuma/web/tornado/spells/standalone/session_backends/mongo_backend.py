# -*- coding: utf-8 -*-

import re
import time
import datetime

import pymongo

from agatsuma import log, Spell
from agatsuma.interfaces import AbstractSpell, InternalSpell
from agatsuma.web.tornado.interfaces import SessionBackendSpell
from agatsuma.web.tornado import BaseSessionManager

"""
Used code from
http://github.com/milancermak/tornado/blob/master/tornado/session.py
"""

"""
class AutoReconnect(object):
    functions = {}
    def __init__(self, method):
        self.method = method

    def __call__(self, *args, **kwargs):
"""

class MongoSessionManager(BaseSessionManager):
    def __init__(self, uri):
        BaseSessionManager.__init__(self)
        self.uri = uri
        self.initConnection()

    def initConnection(self):
        log.sessions.info("Initializing MongoDB session backend using URI '%s'" % self.uri)
        connData = MongoSessionManager._parseMongoTableUri(self.uri)
        mongoSpell = Spell("agatsuma_mongodb")
        self.connection = mongoSpell.connection
        self.dbCollection = getattr(mongoSpell, connData[0])
        self.db = getattr(self.dbCollection, connData[1])
        #self.connection = pymongo.Connection(connData[0], int(connData[1]))
        #self.dbSet = self.connection[connData[2]]
        #self.db = self.dbSet.sessions

    @staticmethod
    def _parseMongoTableUri(details):
        # mongotable://collection/table
        match = re.match('^mongotable://(\w+)/(\w+)$', details)
        return match.group(1), match.group(2)

    def cleanup(self):
        self.db.remove({'expires': {'$lte': int(time.time())}})

    def destroyData(self, session_id):
        try:
            self.db.remove({'session_id': session_id})
            self.connection.end_request()
        except pymongo.errors.AutoReconnect:
            log.sessions.critical("Mongo exception during destroying %s" % session_id)

    def loadData(self, session_id):
        try:
            data = self.db.find_one({'session_id': session_id})
            self.connection.end_request()
            if data:
                return data["data"]
        except pymongo.errors.AutoReconnect:
            log.sessions.critical("Mongo exception during loading %s" % session_id)
        except Exception, e:
            log.sessions.critical("Unknown exception during loading: %s" % str(e))
            self.connection.end_request()

    def saveData(self, session_id, data):
        expTime = int(time.mktime(self._sessionDoomsday(datetime.datetime.now()).timetuple()))
        try:
            self.db.update(
                {'session_id': session_id}, # equality criteria
                {'session_id': session_id,
                'data': data,
                'expires': expTime,
                }, # new document
                upsert=True)
            self.connection.end_request()
        except pymongo.errors.AutoReconnect:
            log.sessions.critical("Mongo exception during saving %s with data %s" % (session_id, str(data)))

class MongoSessionSpell(AbstractSpell, InternalSpell, SessionBackendSpell):
    def __init__(self):
        config = {'info' : 'MongoDB session storage',
                  'deps' : ('agatsuma_mongodb', ),
                  'provides' : ('session_backend', )
                 }
        AbstractSpell.__init__(self, 'tornado_session_backend_mongo', config)

    def instantiateBackend(self, uri):
        self.managerInstance = MongoSessionManager(uri)
        return self.managerInstance

    def preConfigure(self, core):
        core.registerEntryPoint("mongodb:sessions:cleanup", self.entryPoint)

    def entryPoint(self, *args, **kwargs):
        log.core.info("Cleaning old sessions in MongoDB")
        self.managerInstance.cleanup()

