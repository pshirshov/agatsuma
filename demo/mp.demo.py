#!/usr/bin/env python
# -*- coding: utf-8 -*-

import envir # to add upper directory into sys.path, not required for real app

from agatsuma.core import MPCore
from agatsuma import log, Settings, Implementations
from agatsuma.interfaces import AbstractSpell

appRoot = 'demo-minimal'
appConfig = "settings-mp.json"

core = MPCore([appRoot], appConfig,
            appName = "MultiprocessingAgatsumaApp",
            prohibitedSpells = ["agatsuma.spells.common.storage_drivers.core_sqla", # SQLAlchemy is not interesting for this demo
                                ]
            )
core.startSettingsUpdater()

log.newLogger("demo")

log.demo.info("*" * 50)
log.demo.info("Trivial MP application initiated")
allTheSpells = Implementations(AbstractSpell)
log.demo.debug("Here is the all available spells: %s" % str(allTheSpells))

log.demo.info("Option test.test has value: %s" % Settings.test.test)
import random
def randomizeSettings():
    val = u"random_value_%s" % random.randint(0, 9999)
    log.demo.info("Changing value to %s" % val)
    Settings.test.test = val
    Settings.save()

import time
ticks = 0
maxticks = 100
while ticks < maxticks:
    log.demo.info("Iteration %d/%d of useless loop" % (ticks, maxticks))
    ticks += 1
    time.sleep(15)
    randomizeSettings()
