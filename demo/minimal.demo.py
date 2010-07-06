#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import random

import envir # to add upper directory into sys.path, not required for real app

from agatsuma.core import Core
from agatsuma import log, Settings
from agatsuma.interfaces import AbstractSpell
from agatsuma import Implementations

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
log.demo.info("*" * 50)

log.demo.info("Testing interface getters...")
time1 = datetime.datetime.now()
for x in range(0, 100000):
    allTheSpells = Implementations(AbstractSpell)
time2 = datetime.datetime.now()
log.demo.info("Implementations() [cached]        test completed in %s" % str(time2 - time1))

time1 = datetime.datetime.now()
for x in range(0, 100000):
    allTheSpells = Core.instance.implementationsOf(AbstractSpell)
time2 = datetime.datetime.now()
log.demo.info("Core.instance.implementationsOf() test completed in %s" % str(time2 - time1))
log.demo.info("*" * 50)

log.demo.debug("Here is the all available spells: %s" % str(allTheSpells))
log.demo.info("*" * 50)

log.demo.info("Option test.test has value: %s" % Settings.test.test)

val = u"random_value_%s" % random.randint(0, 9999)
log.demo.info("Changing value to %s" % val)
Settings.test.test = val
Settings.save()
log.demo.info("*" * 50)
