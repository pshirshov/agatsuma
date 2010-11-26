# -*- coding: utf-8 -*-

import re
import time
import datetime

import pymongo

from agatsuma import log, Spell

from agatsuma.interfaces import AbstractSpell, IInternalSpell

from agatsuma.commons.types import Atom

from agatsuma.web.tornado.interfaces import ISessionBackendSpell
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
        self.init_connection()

    def init_connection(self):
        log.sessions.info("Initializing MongoDB session backend using URI '%s'" % self.uri)
        connData = MongoSessionManager._parse_mongo_table_uri(self.uri)
        mongoSpell = Spell(Atom.agatsuma_mongodb)
        self.connection = mongoSpell.connection
        self.dbCollection = getattr(mongoSpell, connData[0])
        self.db = getattr(self.dbCollection, connData[1])
        #self.connection = pymongo.Connection(connData[0], int(connData[1]))
        #self.dbSet = self.connection[connData[2]]
        #self.db = self.dbSet.sessions

    @staticmethod
    def _parse_mongo_table_uri(details):
        # mongotable://collection/table
        match = re.match('^mongotable://(\w+)/(\w+)$', details)
        return match.group(1), match.group(2)

    def cleanup(self):
        self.db.remove({'expires': {'$lte': int(time.time())}})

    def destroy_data(self, session_id):
        try:
            self.db.remove({'session_id': session_id})
            self.connection.end_request()
        except pymongo.errors.AutoReconnect:
            log.sessions.critical("Mongo exception during destroying %s" % session_id)

    def load_data(self, session_id):
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

    def save_data(self, session_id, data):
        expTime = int(time.mktime(self._session_doomsday(datetime.datetime.now()).timetuple()))
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

class MongoSessionSpell(AbstractSpell, IInternalSpell, ISessionBackendSpell):
    def __init__(self):
        config = {'info' : 'MongoDB session storage',
                  'deps' : (Atom.agatsuma_mongodb, ),
                  'provides' : (Atom.session_backend, )
                 }
        AbstractSpell.__init__(self, Atom.tornado_session_backend_mongo, config)

    def instantiate_backend(self, uri):
        self.managerInstance = MongoSessionManager(uri)
        return self.managerInstance

    def pre_configure(self, core):
        core.register_entry_point("mongodb:sessions:cleanup", self.entry_point)

    def entry_point(self, *args, **kwargs):
        log.core.info("Cleaning old sessions in MongoDB")
        self.managerInstance.cleanup()
