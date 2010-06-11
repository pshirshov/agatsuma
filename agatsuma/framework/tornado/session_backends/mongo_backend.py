# -*- coding: utf-8 -*-

import pymongo
import re
import time
import datetime

from agatsuma.log import log
from agatsuma.settings import Settings
from agatsuma.core import Core
from agatsuma.interfaces import AbstractSpell
from agatsuma.framework.tornado import SessionBackendSpell
from agatsuma.framework.tornado import BaseSessionManager


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
        connData = self._parse_connection_details(self.uri)
        mongoSpell = Core.instance.spellsDict["agatsuma_mongodb"]
        self.db = mongoSpell.agatsuma_sessions
        #self.connection = pymongo.Connection(connData[0], int(connData[1]))
        #self.dbSet = self.connection[connData[2]]
        #self.db = self.dbSet.sessions
        
    @staticmethod
    def _parse_connection_details(details):
        match = re.match('^mongotable://(\w+)$', details)
        return match.group(1)

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
            log.sessions.critical("Unknown exception during loading %s" % str(e))
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
            
class MongoSessionSpell(AbstractSpell, SessionBackendSpell):
    def __init__(self):
        config = {'info' : 'MongoDB session storage',
                  'deps' : ('agatsuma_mongodb', 'agatsuma_session', )
                 }
        AbstractSpell.__init__(self, 'tornado_session_backend_mongo', config)
        
    def instantiateBackend(self, uri):
        self.managerInstance = MongoSessionManager(uri)
        return self.managerInstance

    def preConfigure(self, core):
        core.registerEntryPoint("mongodb:sessions:cleanup", self.entryPoint)
        
    def entryPoint(self, argv):
        log.core.info("Cleaning old sessions in MongoDB")
        self.managerInstance.cleanup()

class MongoDBSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'MongoDB support',
                  'deps' : ()
                 }
        AbstractSpell.__init__(self, 'agatsuma_mongodb', config)
        
    def preConfigure(self, core):
        core.registerOption("!mongo.uri", unicode, "MongoDB host URI")
        core.registerOption("!mongo.databases", list, "MongoDB databases to use")

    def postConfigure(self, core):
        self.initConnection()
        
    def initConnection(self):
        log.core.info("Initializing MongoDB connections on URI '%s'" % Settings.mongo.uri)
        connData = self._parse_connection_details(Settings.mongo.uri)
        self.connection = pymongo.Connection(connData[0], int(connData[1]))
        for dbName in Settings.mongo.databases:
            assert type(dbName) is unicode
            setattr(self, dbName, self.connection[dbName])
        
    @staticmethod
    def _parse_connection_details(details):
        # mongodb://[host[:port]]/db
        match = re.match(r'^mongodb://([\S|\.]+?)?(?::(\d+))?$', details)
        return  match.group(1), match.group(2) #, match.group(3) # host, port, database
        
