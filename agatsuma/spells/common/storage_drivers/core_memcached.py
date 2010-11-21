# -*- coding: utf-8 -*-
from agatsuma.core import Core
if Core.internal_state.get("mode", None) == "normal":
    import pylibmc
import re

from agatsuma.log import log
from agatsuma.settings import Settings

from agatsuma.interfaces import AbstractSpell, InternalSpell
from agatsuma.interfaces import StorageSpell, SetupSpell

from agatsuma.elements import Atom

class MemcachedSpell(AbstractSpell, InternalSpell, StorageSpell, SetupSpell):
    def __init__(self):
        config = {'info' : 'Memcached support',
                  'deps' : (),
                  'provides': (Atom.storage_driver, ),
                 }
        AbstractSpell.__init__(self, Atom.agatsuma_memcached, config)

    def pre_configure(self, core):
        core.register_option("!memcached.uri", unicode, "Memcached host URI")
        core.register_option("!memcached.behaviors", dict,
                            "Memcached additional parameters")

    def post_configure(self, core):
        self.init_connection()

    def init_connection(self):
        log.storage.info("Initializing Memcached connections on URI '%s'" % \
                      Settings.memcached.uri)
        connData = self._parse_memcached_uri(Settings.memcached.uri)
        print connData
        self._connection = pylibmc.Client([":".join(connData)])
        self._connection.behaviors = Settings.memcached.behaviors
        self._pool = pylibmc.ThreadMappedPool(self._connection)

    def get_connection_pool(self):
        return self._pool

    @staticmethod
    def _parse_memcached_uri(uri):
        # memcached://host:port
        match = re.match(r'^memcached://([\S|\.]+?)?(?::(\d+))?$', uri)
        if match and match.group(2):
            return  match.group(1), match.group(2) # host, port
        return  match.group(1)

    def requirements(self):
        return {"memcache" : ["pylibmc>=1.1.1", ],
               }
