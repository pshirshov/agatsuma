# -*- coding: utf-8 -*-
from agatsuma.core import Core
if Core.internalState.get("mode", None) == "normal":
    import pylibmc
import re

from agatsuma.log import log
from agatsuma.settings import Settings
from agatsuma.interfaces import AbstractSpell, InternalSpell
from agatsuma.interfaces import StorageSpell, SetupSpell

class MemcachedSpell(AbstractSpell, InternalSpell, StorageSpell, SetupSpell):
    def __init__(self):
        config = {'info' : 'Memcached support',
                  'deps' : (),
                  'provides': ('storage_driver', ),
                 }
        AbstractSpell.__init__(self, 'agatsuma_memcached', config)

    def preConfigure(self, core):
        core.registerOption("!memcached.uri", unicode, "Memcached host URI")
        core.registerOption("!memcached.behaviors", dict,
                            "Memcached additional parameters")

    def postConfigure(self, core):
        self.initConnection()

    def initConnection(self):
        log.storage.info("Initializing Memcached connections on URI '%s'" % \
                      Settings.memcached.uri)
        connData = self._parseMemcachedUri(Settings.memcached.uri)
        print connData
        self._connection = pylibmc.Client([":".join(connData)])
        self._connection.behaviors = Settings.memcached.behaviors
        self._pool = pylibmc.ThreadMappedPool(self._connection)

    def getConnectionPool(self):
        return self._pool

    @staticmethod
    def _parseMemcachedUri(uri):
        # memcached://host:port
        match = re.match(r'^memcached://([\S|\.]+?)?(?::(\d+))?$', uri)
        if match and match.group(2):
            return  match.group(1), match.group(2) # host, port
        return  match.group(1)

    def requirements(self):
        return {"memcache" : ["pylibmc>=1.1.1", ],
               }
