# -*- coding: utf-8 -*-

import re

from agatsuma.log import log
from agatsuma.core import Core
from agatsuma.interfaces import AbstractSpell, SettingsBackendSpell, SettingsBackend

class MongoSettingsBackend(SettingsBackend):
    def __init__(self, uri):
        self.uri = uri
        self.initConnection()

    def initConnection(self):
        log.core.info("Initializing MongoDB settings backend using URI '%s'" % self.uri)
        connData = MongoSettingsBackend._parseMongoTableUri(self.uri)
        mongoSpell = Core.instance.spellsDict["agatsuma_mongodb"]
        self.connection = mongoSpell.connection
        self.dbCollection = getattr(mongoSpell, connData[0])
        self.db = getattr(self.dbCollection, connData[1])

    @staticmethod
    def _parseMongoTableUri(details):
        # mongotable://collection/table
        match = re.match('^mongotable://(\w+)/(\w+)$', details)
        return match.group(1), match.group(2)

    def get(self, name, currentValue):
        try:
            data = self.db.find_one({'name': name})
            self.connection.end_request()
            if data:
                return data["value"]
        except pymongo.errors.AutoReconnect:
            log.core.critical("Mongo exception during loading %s" % name)
        except Exception, e:
            log.core.critical("Unknown exception during loading: %s" % str(e))
            self.connection.end_request()
        return currentValue

    def save(self, name, value):
        try:
            self.db.update(
                {'name': name}, # equality criteria
                {'name' : name,
                 'value': value,
                }, # new document
                upsert=True)
            self.connection.end_request()
        except pymongo.errors.AutoReconnect:
            log.core.critical("Mongo exception during saving %s=%s" % (name, str(value)))

class MongoSettingsSpell(AbstractSpell, SettingsBackendSpell):
    def __init__(self):
        config = {'info' : 'MongoDB settings storage',
                  'deps' : ('agatsuma_mongodb', ),
                  'provides' : ('settings_backend', )
                 }
        AbstractSpell.__init__(self, 'tornado_settings_backend_mongo', config)

    def instantiateBackend(self, uri):
        self.managerInstance = MongoSettingsBackend(uri)
        return self.managerInstance

    def preConfigure(self, core):
        core.registerEntryPoint("mongodb:settings:cleanup", self.entryPoint)

    def entryPoint(self, argv):
        log.core.info("Cleaning up settings in MongoDB")
        self.managerInstance.cleanup()

