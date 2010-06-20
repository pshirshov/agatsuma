# -*- coding: utf-8 -*-
import pylibmc
import re

from agatsuma.log import log
from agatsuma.settings import Settings
from agatsuma.interfaces import AbstractSpell

class MemcachedSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Memcached support',
                  'deps' : ()
                  'provides': ('storage_driver', ),
                 }
        AbstractSpell.__init__(self, 'agatsuma_memecached', config)

    def preConfigure(self, core):
        core.registerOption("!memcached.uri", unicode, "Memcached host URI")
        core.registerOption("!memcached.behaviors", dict,
                            "Memcached additional parameters")

    def postConfigure(self, core):
        self.initConnection()

    def initConnection(self):
        log.core.info("Initializing Memecache connections on URI '%s'" % \
                      Settings.memcached.uri)
        connData = self._parseMemcachedUri(Settings.memcached.uri)
        self._connection = pylibmc.Client(":".join(connData))
        self._connection.behaviors = Settings.memcached.behaviors
        self._pool = pylibmc.ThreadMappedPool(self._connection)

    @property
    def connection():
        with self._pool.reserve() as mc:
            return mc

    @staticmethod
    def _parseMemcachedUri(uri):
        # memcached://host:port
        match = re.match(r'^memcached://([\S|\.]+?)?(?::(\d+))?$', uri)
        if match and match.group(2):
            return  match.group(1), match.group(2) # host, port
        return  match.group(1)
