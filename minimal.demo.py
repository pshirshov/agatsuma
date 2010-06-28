#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from agatsuma.core import Core
from agatsuma import log, Settings
from agatsuma.interfaces import AbstractSpell

appRoot = 'demo-minimal'
appConfig = "settings-minimal.json"

core = Core([appRoot], appConfig,
            appName = "MinimalAgatsumaApp",
            prohibitedSpells = ["agatsuma.spells.common.storage_drivers.core_sqla", # SQLAlchemy is not interesting for this demo
                                ] 
            )

log.newLogger("demo")

log.demo.info("*" * 50)
log.demo.info("Trivial application initiated")
allTheSpells = core.implementationsOf(AbstractSpell)
log.demo.debug("Here is the all available spells: %s" % str(allTheSpells))

log.demo.info("Option test.test has value: %s" % Settings.test.test)
import random
val = u"random_value_%s" % random.randint(0, 9999)
log.demo.info("Changing value to %s" % val)
Settings.test.test = val
Settings.save()
