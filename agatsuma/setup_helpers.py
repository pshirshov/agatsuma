# -*- coding: utf-8 -*-

from agatsuma import Implementations
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

def getEntryPoints():
    entryPointsDict = collectEntryPoints()
    return formatEntryPoints(entryPointsDict)

def depinfo(groupChecker):
    spells = Implementations(SetupSpell)
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
            if groupChecker(group):
                dependencies.extend(deps)
    dependencies = list(set(dependencies))
    return dependencies, depGroups, depGroupsContent

def runSetuptools(**kwargs):
    from setuptools import setup
    from distribute_setup import use_setuptools
    use_setuptools()
    setup(**kwargs)
