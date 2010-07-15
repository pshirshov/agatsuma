#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from agatsuma.core import Core
from agatsuma.setup_helpers import getEntryPoints, depinfo, runSetuptools
#from agatsuma import Implementations
#from agatsuma.interfaces import SetupSpell

if __name__ == '__main__':
    #from agatsuma import log
    def out(s):
        #log.setup.info
        print s

    def line():
        out("="*25)

    #import logging
    #log.newLogger("setup", logging.DEBUG)
    out("\nAgatsuma: Distribute mode")
    line()

    core = Core(None, None, appMode = 'setup')
    entryPoints = getEntryPoints()

    line()
    out("The following entry points are provided: %s" % entryPoints)
    line()

    components = filter(lambda s: s.startswith('--with'), sys.argv)
    sys.argv = filter(lambda s: not s.startswith('--with'), sys.argv)

    depsDisabled = "--disable-all" in sys.argv
    sys.argv = filter(lambda s: s != "--disable-all", sys.argv)

    def depGroupEnabled(group):
        depEnabled =(not (depsDisabled or ('--without-%s' % group) in components)
                     or (depsDisabled and ('--with-%s' % group) in components))
        return depEnabled

    dependencies, depGroups, depGroupsContent = depinfo(depGroupEnabled)

    out("The following dependencies classes are present:")
    out("(Use --disable-all to disable all the dependencies)")
    for group in depGroups:
        formatString = "[ ] %s: %s "
        if depGroupEnabled(group):
            formatString = "[*] %s: %s"
        out(formatString % (group, str(depGroupsContent[group])))
        out("    Use --without-%s to disable" % group)
        out("    Use --with-%s to enable" % group)
    line()
    out("The following dependencies list will be used:\n%s" % str(dependencies))

################################################################################
    out("\nContinuing with Distribute...\n")
    from setuptools import find_packages
    runSetuptools(
        name = "Agatsuma",
        version = Core.versionString,
        packages = find_packages(exclude=['distribute_setup']),
        install_requires = dependencies,
        entry_points = entryPoints,

        zip_safe=False,
        include_package_data = True,

        #scripts = ['say_hello.py'],

        #test_suite = 'nose.collector',
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
################################################################################
