# -*- coding: utf-8 -*-

from agatsuma import Implementations
from agatsuma.interfaces import ISetupSpell, IInternalSpell

def run_setuptools(**kwargs):
    from setuptools import setup
    from agatsuma.third_party.distribute_setup import use_setuptools
    use_setuptools()
    setup(**kwargs)

######################################################################
## Entry points
def collectEntryPoints(spells_filter):
    spells = Implementations(ISetupSpell)
    spells = filter(spells_filter, spells)
    sections = {}
    for spell in spells:
        pointsdict = spell.py_entry_points()
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

def entry_pointsInfo(spells_filter):
    entry_pointsDict = collectEntryPoints(spells_filter)
    return formatEntryPoints(entry_pointsDict)

######################################################################
## Dependencies
def __withoutIInternalSpells(spell):
    return not issubclass(type(spell), IInternalSpell)

def depinfo(groupChecker, spells_filter):
    spells = Implementations(ISetupSpell)
    spells = filter(spells_filter, spells)
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

######################################################################
## Debug printouts
def out(s):
    #log.setup.info
    print s

def nl():
    out("="*60)

def printDeps(dependencies, depGroups, depGroupsContent, depGroupEnabled):
    out("The following dependencies classes are present:")
    out("(Use --disable-all to disable all the dependencies)")
    for group in depGroups:
        formatString = "[ ] %s: %s "
        if depGroupEnabled(group):
            formatString = "[*] %s: %s"
        out(formatString % (group, str(depGroupsContent[group])))
        out("    Use --without-%s to disable" % group)
        out("    Use --with-%s to enable" % group)
    nl()
    out("The following dependencies list will be used:\n%s" % str(dependencies))
    out("NOTE: You can use AGATSUMA_CONF environment variable to pass options")
    out("NOTE: Dependencies may not work under easy_setup. Use pip!")
######################################################################
## Useful routines
def filter_arguments(args):
    args = filter(lambda s: not s.startswith('--with'), args)
    args = filter(lambda s: s != "--disable-all", args)
    return args

def groups_predicate(args):
    components = filter(lambda s: s.startswith('--with'), args)
    depsDisabled = "--disable-all" in args

    def depGroupEnabled(group):
        depEnabled =(not (depsDisabled or ('--without-%s' % group) in components)
                     or (depsDisabled and ('--with-%s' % group) in components))
        return depEnabled
    return depGroupEnabled

def get_dependencies(depGroupsFilter, spells_filter = __withoutIInternalSpells):
    dependencies, depGroups, depGroupsContent = depinfo(depGroupsFilter,
                                                        spells_filter)
    printDeps(dependencies, depGroups, depGroupsContent, depGroupsFilter)
    return dependencies

def get_entry_points(spells_filter = __withoutIInternalSpells):
    entry_points = entry_pointsInfo(spells_filter)
    nl()
    out("The following entry points are provided: %s" % entry_points)
    nl()
    return entry_points

