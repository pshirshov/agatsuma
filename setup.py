#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import logging
import sys

from agatsuma.core import Core
from agatsuma import Implementations
#from agatsuma import log
from agatsuma.interfaces import SetupSpell

def collectEntryPoints():
    spells = Implementations(SetupSpell)
    sections = {}
    for spell in spells:
        pointsdict = spell.pyEntryPoints()
        for section in pointsdict:
            if not sections.get(section, None):
                sections[section] = []
            points = pointsdict[section]
            sections[section].extend(points)
    return sections

def formatEntryPoints(epoints):
    out = ""
    for section, points in epoints.items():
        out += "[%s]\n" % section
        for point in points:
            out += "%s = %s:%s\n" % (point[0], point[1], point[2])
    return out

def out(s):
    #log.setup.info
    print s

def line():
    out("="*25)

if __name__ == '__main__':
    components = filter(lambda s: s.startswith('--with'), sys.argv)
    sys.argv = filter(lambda s: not s.startswith('--with'), sys.argv)

    depsDisabled = "--disable-all" in sys.argv
    sys.argv = filter(lambda s: s != "--disable-all", sys.argv)

    core = Core(None, None, appMode = 'setup')
    #log.newLogger("setup", logging.DEBUG)
    spells = Implementations(SetupSpell)

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

    out("\nAgatsuma: Distribute mode")
    line()
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
    dependencies = list(set(dependencies))
    out("The following dependencies list will be used:\n%s" % str(dependencies))

    line()
    entryPointsDict = collectEntryPoints()
    entryPoints = formatEntryPoints(entryPointsDict)
    out("The following entry points are provided: %s" % entryPoints)
    line()

################################################################################
    out("\nContinuing with Distribute...\n")

    from setuptools import setup, find_packages
    from distribute_setup import use_setuptools

    use_setuptools()
    setup(
        name = "Agatsuma",
        version = Core.versionString,
        packages = find_packages(),
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
