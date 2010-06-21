import pymongo
import re

from agatsuma.log import log
from agatsuma.settings import Settings
from agatsuma.interfaces import AbstractSpell, StorageSpell

class MongoDBSpell(AbstractSpell, StorageSpell):
    def __init__(self):
        config = {'info' : 'MongoDB support',
                  'deps' : (),
                  'provides': ('storage_driver', ),
                 }
        AbstractSpell.__init__(self, 'agatsuma_mongodb', config)

    def preConfigure(self, core):
        core.registerOption("!mongo.uri", unicode, "MongoDB host URI")
        core.registerOption("!mongo.db_collections", list, "MongoDB databases to use")

    def postConfigure(self, core):
        self.initConnection()

    def initConnection(self):
        log.core.info("Initializing MongoDB connections on URI '%s'" % Settings.mongo.uri)
        connData = MongoDBSpell._parseMongoUri(Settings.mongo.uri)
        self.connection = pymongo.Connection(connData[0], connData[1])
        for dbCollectionName in Settings.mongo.db_collections:
            assert type(dbCollectionName) is unicode
            setattr(self, dbCollectionName, self.connection[dbCollectionName])

    @staticmethod
    def _parseMongoUri(uri):
        # mongodb://host:port
        match = re.match(r'^mongodb://([\S|\.]+?)?(?::(\d+))?$', uri)
        if match.group(2):
            return  match.group(1), int(match.group(2)) # host, port
        return  match.group(1), None
