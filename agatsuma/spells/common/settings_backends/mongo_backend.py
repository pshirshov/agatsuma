# -*- coding: utf-8 -*-

import re

import pymongo

from agatsuma import log
from agatsuma import Spell
from agatsuma.interfaces import AbstractSpell, IInternalSpell
from agatsuma.interfaces import ISettingsBackendSpell, AbstractSettingsBackend

from agatsuma.commons.types import Atom

class MongoAbstractSettingsBackend(AbstractSettingsBackend):
    def __init__(self, uri):
        self.uri = uri
        self.init_connection()

    def init_connection(self):
        log.settings.info("Initializing MongoDB settings backend using URI '%s'" % self.uri)
        connData = MongoAbstractSettingsBackend._parse_mongo_table_uri(self.uri)
        mongoSpell = Spell(Atom.agatsuma_mongodb)
        self.connection = mongoSpell.connection
        self.dbCollection = getattr(mongoSpell, connData[0])
        self.db = getattr(self.dbCollection, connData[1])

    @staticmethod
    def _parse_mongo_table_uri(details):
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
            log.settings.critical("Mongo exception during loading %s" % name)
        except Exception, e:
            log.settings.critical("Unknown exception during loading: %s" % str(e))
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
            log.settings.critical("Mongo exception during saving %s=%s" % (name, str(value)))

class MongoSettingsSpell(AbstractSpell, IInternalSpell, ISettingsBackendSpell):
    def __init__(self):
        config = {'info' : 'MongoDB settings storage',
                  'deps' : (Atom.agatsuma_mongodb, ),
                  'provides' : (Atom.settings_backend, )
                 }
        AbstractSpell.__init__(self, Atom.agatsuma_settings_backend_mongo, config)

    def instantiate_backend(self, uri):
        self.managerInstance = MongoAbstractSettingsBackend(uri)
        return self.managerInstance

    def pre_configure(self, core):
        core.register_entry_point("mongodb:settings:cleanup", self.entry_point)

    def entry_point(self, *args, **kwargs):
        log.settings.info("Cleaning up settings in MongoDB")
        self.managerInstance.cleanup()
