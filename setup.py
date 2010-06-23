#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from setuptools import setup, find_packages
from distribute_setup import use_setuptools

from agatsuma.core import Core
from agatsuma import log
from agatsuma.interfaces import AbstractSpell

use_setuptools()

core = Core(None, None, appMode = 'setup')
log.newLogger("setup", logging.DEBUG)
spells = core.implementationsOf(AbstractSpell)

def depGroupEnabled(depdicts):
    return True

depGroups = []
dependencies = []
for spell in spells:
    depdict = spell.requirements()
    for group in depdict:
        depGroups.append(group)
        if depGroupEnabled(group):
            dependencies.append(depdict[group])

log.setup.info("The following dependencies classes are present")
for group in depGroups:
    formatString = " %s "
    if depGroupEnabled:
        formatString = "[%s]" 
    log.setup.info(formatString % group)

log.setup.info("The following dependencies list will be used: %s" % str(dependencies))

setup(
    name = "Agatsuma",
    version = Core.versionString,
    packages = find_packages(),
    install_requires = dependencies,

    #scripts = ['say_hello.py'],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        #'hello': ['*.msg'],
    },

    # metadata for upload to PyPI
    author = "Fei Wong Reed",
    author_email = "feiwreed@gmail.com",
    description = "Modularity and flexibility for Tornado and others",
    license = "GPL3",
    keywords = "agatsuma modularity web framework dynamic imports",
    url = "http://agatsuma.ritsuka.org/",
)
