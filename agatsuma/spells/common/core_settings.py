# -*- coding: utf-8 -*-

import re
import copy

from agatsuma import log
from agatsuma import Settings
from agatsuma import SpellByStr
from agatsuma.interfaces import AbstractSpell, InternalSpell

from agatsuma.elements import Atom

class SettingsSpell(AbstractSpell, InternalSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Settings Spell',
                  'deps' : (),
                  'requires' : (Atom.settings_backend, ),
                 }
        AbstractSpell.__init__(self, Atom.agatsuma_settings, config)

    def pre_configure(self, core):
        log.new_logger("settings")
        core.register_option("!core.settings_storage_uri", unicode, "Settings storage URI")
        core.register_option("!core.recovery", bool, "Recovery mode")

    def post_configure(self, core):
        Settings.save = self.save
        log.core.debug('Settings.save method overriden')
        storageUri = Settings.core.settings_storage_uri
        recovery = Settings.recovery or Settings.core.recovery
        self.backend = None
        if not recovery:
            log.settings.info("Initializing Settings Storage..")
            rex = re.compile(r"^(\w+)\+(.*)$")
            match = rex.match(storageUri)
            if match:
                backendId = match.group(1)
                uri = match.group(2)
                spellName = "agatsuma_settings_backend_%s" % backendId
                spell = SpellByStr(spellName)
                if spell:
                    self.backend = spell.instantiate_backend(uri)
                else:
                    raise Exception("Settings backend improperly configured: spell '%s' not found" % spellName)
            else:
                raise Exception("Incorrect settings storage URI")
        else:
            log.settings.warning("Running in recovery mode, settings in storage are ignored")

        if self.backend:
            log.settings.info("Updating writable settings from storage '%s'..." % self.backend.__class__.__name__)
            updated = 0
            for groupName in Settings.settings:
                group = Settings.settings[groupName]
                newGroup = copy.deepcopy(group)
                updatedInGroup = 0
                for setting in group:
                    if not setting in Settings.readonly_settings[groupName]:
                        curVal = group[setting]
                        newVal = self.backend.get("%s.%s" % (groupName, setting), curVal)
                        if newVal != curVal:
                            newGroup[setting] = newVal
                            updated += 1
                            updatedInGroup += 1
                    if updatedInGroup:
                        Settings.settings[groupName] = newGroup
            if updated:
                Settings.set_config_data(Settings.settings)
            log.settings.info("Settings updated from storage: %d" % updated)

    def save(self):
        log.settings.info("Writing settings into storage '%s'..." % self.backend.__class__.__name__)
        written = 0
        for groupName in Settings.settings:
            group = Settings.settings[groupName]
            for setting in group:
                if not setting in Settings.readonly_settings[groupName]:
                    self.backend.save("%s.%s" % (groupName, setting), group[setting])
                    written += 1
        log.settings.info("Settings written into storage: %d" % written)
