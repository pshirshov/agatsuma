# -*- coding: utf-8 -*-

import re
import copy

from agatsuma.log import log
from agatsuma.settings import Settings
from agatsuma.interfaces.abstract_spell import AbstractSpell

class SettingsSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Settings Spell',
                  'deps' : (),
                  'requires' : ('settings_backend', ),
                 }
        AbstractSpell.__init__(self, 'agatsuma_settings', config)

    def preConfigure(self, core):
        import logging
        log.newLogger("settings", logging.DEBUG)
        core.registerOption("!core.settings_storage_uri", unicode, "Settings storage URI")
        core.registerOption("!core.recovery", bool, "Recovery mode")

    def postConfigure(self, core):
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
                from agatsuma.core import Core
                spell = Core.instance.spellsDict.get(spellName, None)
                if spell:
                    self.backend = spell.instantiateBackend(uri)
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
                    if not setting in Settings.roSettings[groupName]:
                        curVal = group[setting]
                        newVal = self.backend.get("%s.%s" % (groupName, setting), curVal)
                        if newVal != curVal:
                            newGroup[setting] = newVal
                            updated += 1
                            updatedInGroup += 1
                    if updatedInGroup:
                        Settings.settings[groupName] = newGroup
            if updated:
                Settings.setConfigData(Settings.settings)
            log.settings.info("Settings updated from storage: %d" % updated)

    def save(self):
        log.settings.info("Writing settings into storage '%s'..." % self.backend.__class__.__name__)
        written = 0
        for groupName in Settings.settings:
            group = Settings.settings[groupName]
            for setting in group:
                if not setting in Settings.roSettings[groupName]:
                    self.backend.save("%s.%s" % (groupName, setting), group[setting])
                    written += 1
        log.settings.info("Settings written into storage: %d" % written)
