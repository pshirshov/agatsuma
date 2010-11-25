# -*- coding: utf-8 -*-
import re

try:
    import cPickle as pickle
except ImportError:
    import pickle

from agatsuma import log
from agatsuma import Spell
from agatsuma.interfaces import (AbstractSpell,
                                 IInternalSpell,
                                 ISettingsBackendSpell,
                                 AbstractSettingsBackend)

from agatsuma.commons.types import Atom

class MemcachedAbstractSettingsBackend(AbstractSettingsBackend):
    def __init__(self, uri):
        AbstractSettingsBackend.__init__(self)
        self.uri = uri
        self.init_connection()

    def init_connection(self):
        log.settings.info("Initializing Memcached settings backend "\
                          "using URI '%s'" % self.uri)
        self.keyprefix = self._parse_memcached_prefix_uri(self.uri)
        memcachedSpell = Spell(Atom.agatsuma_memcached)
        self.pool = memcachedSpell.get_connection_pool()

    @property
    def connection(self):
        with self.pool.reserve() as mc:
            return mc

    def _getPrefixedKey(self, sessionId):
        if self.keyprefix:
            return str("%s_%s" % (self.keyprefix, sessionId))
        return sessionId

    @staticmethod
    def _parse_memcached_prefix_uri(details):
        # memprefix://prefixname
        match = re.match('^memprefix://(\w+)$', details)
        return match.group(1) if match else ''

    def get(self, name, currentValue):
        data = self.connection.get(self._getPrefixedKey(name))
        if data:
          return pickle.loads(data)
        return currentValue

    def save(self, name, value):
        if not self.connection.set(self._getPrefixedKey(name),
                                   pickle.dumps(value)):
            log.settings.critical("Saving setting '%s' failed" % name)

class MemcachedSettingsSpell(AbstractSpell, IInternalSpell, ISettingsBackendSpell):
    def __init__(self):
        config = {'info' : 'Memcached settings storage',
                  'deps' : (Atom.agatsuma_memcached, ),
                  'provides' : (Atom.settings_backend, )
                 }
        AbstractSpell.__init__(self, Atom.agatsuma_settings_backend_memcached,
                               config)

    def instantiate_backend(self, uri):
        self.managerInstance = MemcachedAbstractSettingsBackend(uri)
        return self.managerInstance
