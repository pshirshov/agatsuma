#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import logging
import sys

from agatsuma.core import Core
#from agatsuma import log
from agatsuma.interfaces import AbstractSpell

components = filter(lambda s: s.startswith('--with'), sys.argv)
sys.argv = filter(lambda s: not s.startswith('--with'), sys.argv)

depsDisabled = "--disable-all" in sys.argv
sys.argv = filter(lambda s: s != "--disable-all", sys.argv)

core = Core(None, None, appMode = 'setup')
#log.newLogger("setup", logging.DEBUG)
spells = core.implementationsOf(AbstractSpell)

def depGroupEnabled(group):
    depEnabled =(not (depsDisabled or ('--without-%s' % group) in components)
                 or (depsDisabled and ('--with-%s' % group) in components))
    return depEnabled

depGroups = []
dependencies = []
depGroupsContent = {}
for spell in spells:
    depdict = spell.requirements()
    for group in depdict:
        depGroups.append(group)
        if not depGroupsContent.get(group, None):
            depGroupsContent[group] = []
        deps = depdict[group]
        depGroupsContent[group].extend(deps)
        if depGroupEnabled(group):
            dependencies.extend(deps)
def out(s):
    #log.setup.info
    print s

out("\nAgatsuma: Distribute mode\n")
out("The following dependencies classes are present:")
out("(User --disable-all to disable all the dependencies)")
for group in depGroups:
    formatString = "[ ] %s: %s "
    if depGroupEnabled(group):
        formatString = "[*] %s: %s" 
    out(formatString % (group, str(depGroupsContent[group])))
    out("    Use --without-%s to disable" % group)
    out("    Use --with-%s to enable" % group)

out("The following dependencies list will be used: %s" % str(dependencies))

out("\nContinuing with Distribute...\n")

from setuptools import setup, find_packages
from distribute_setup import use_setuptools

use_setuptools()
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
