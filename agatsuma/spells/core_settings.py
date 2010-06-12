# -*- coding: utf-8 -*-

import re
import copy

from agatsuma.log import log
from agatsuma.settings import Settings
from agatsuma.interfaces.abstract_spell import AbstractSpell
        
class SettingsSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Settings Spell',
                  'deps' : ()
                 }
        AbstractSpell.__init__(self, 'agatsuma_settings', config)
        
    def preConfigure(self, core):
        core.registerOption("!core.settings_storage_uri", unicode, "Settings storage URI")
        core.registerOption("!core.recovery", bool, "Recovery mode")
        
    def prePoolInit(self, core):
        storageUri = Settings.core.settings_storage_uri
        recovery = Settings.recovery or Settings.core.recovery
        self.backend = None
        if not recovery:
            log.core.info("Initializing Settings Storage..")
            rex = re.compile(r"^(\w+)\+(.*)$")
            match = rex.match(storageUri)
            if match:
                backendId = match.group(1)
                uri = match.group(2)
                spellName = "tornado_settings_backend_%s" % backendId
                from agatsuma.core import Core
                spell = Core.instance.spellsDict[spellName]
                self.backend = spell.instantiateBackend(uri)
            else:
                raise Exception("Incorrect settings storage URI")
        else:
            log.core.warning("Running in recovery mode, settings in storage are ignored")

        if self.backend:
            log.core.info("Updating writable settings from storage...")
            updated = 0
            for groupName in Settings.settings:
                group = Settings.settings[groupName]
                newGroup = copy.deepcopy(group)
                updatedInGroup = 0
                for setting in group:
                    if not setting in Settings.roSettings[groupName]:
                        curVal = group[setting]
                        newVal = self.backend.get("%s.%s" % (groupName, setting), curVal)
                        print curVal, "<>", newVal
                        if newVal != curVal:
                            newGroup[setting] = newVal
                            updated += 1
                            updatedInGroup += 1
                    if updatedInGroup:
                        Settings.settings[groupName] = newGroup
            if updated:
                Settings.setConfigData(Settings.settings)
            log.core.info("Settings updated from storage: %d" % updated)
