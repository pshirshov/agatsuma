# -*- coding: utf-8 -*-

import sys
import os
import inspect
import re
#import traceback

from agatsuma.log import log
from agatsuma.interfaces import AbstractSpell, InternalSpell

def alist_to_strlist(alist):
    return map(lambda atom: str(atom), alist)

class Enumerator(object):
    def __init__(self, core, app_directorys, forbidden_spells):
        self.app_directorys = app_directorys
        self.forbidden_spells = forbidden_spells
        self.core = core
        #def appBaseName(self):
        #  return self.__module__.split('.')[0]

    def __register_spell(self, spell):
        self.core.spells.append(spell)
        self.core.spellbook[spell.spell_id()] = spell

    def __unregister_spell(self, spell):
        self.core.spells.remove(spell)
        del self.core.spellbook[spell.spell_id()]

    def enumerate_spells(self, essentialSpellSpaces, additionalSpellPaths):
        spell_directories = []
        spell_directories.extend(additionalSpellPaths)

        if self.app_directorys:
            spell_directories.extend(self.app_directorys)
            if not self.core.app_name:
                log.core.warning("Application name not provided, so trying to guess one...")
                print self.app_directorys
                if type(self.app_directorys[0]) == str:
                    self.core.app_name = self.app_directorys[0][0].capitalize() + self.app_directorys[0][1:]
                else:
                    self.core.app_name = self.app_directorys[0][1][0].capitalize() + self.app_directorys[0][1][1:]
                log.core.info('Guessed name: %s' % self.core.app_name)
        else:
            log.core.critical("No main spellpaths to process provided")
            if self.core.internal_state.get('mode') == 'setup':
                log.core.info("Setup mode detected, so replacing all the spellpaths with Agatsuma itself...")
                spell_directories = [(os.path.join(self.core.agatsuma_base_dir, 'agatsuma'), 'agatsuma')]
        log.core.debug("Spellpaths to process:")
        for p in spell_directories:
            log.core.debug("* %s" % str(p))

        log.core.debug("System paths:")
        for p in sys.path:
            log.core.debug("* %s" % p)
        log.core.info("Collecting names of possible spells...")

        namespacesToImport = []
        namespacesToImport.extend(essentialSpellSpaces)

        for spellsDir in spell_directories:
            #spellsDir =  #os.path.realpath(os.path.join(self.OPT.appPath, 'controllers'))
            #sys.path.append(spellsDir)

            if not type(spellsDir) is tuple:
                basicNamespace = spellsDir.replace(os.path.sep, '.') #os.path.basename(spellsDir)
            else:
                basicNamespace = spellsDir[1]
                spellsDir = spellsDir[0]

            log.core.info("Processing spells directory: %s" % spellsDir)
            log.core.info("Spells namespace: %s" % basicNamespace)

            for root, dirs, files in os.walk(spellsDir):
                def useFilePred(file):
                    if file in self.forbidden_spells:
                        log.core.warning('File ignored due app settings: %s' % file)
                        return False
                    return True
                fileList = filter(lambda x: x.endswith('.py') and not x.startswith('__'), files)
                fileList = filter(useFilePred, fileList)
                fileList = map(lambda x: os.path.join(root, x), fileList)
                fileList = map(lambda x: os.path.splitext(x)[0], fileList)
                fileList = map(lambda x: x.replace(spellsDir + os.path.sep, ''), fileList)
                fileList = map(lambda x: x.replace(os.path.sep, '.'), fileList)
                fileList = map(lambda x: "%s.%s" % (basicNamespace, x), fileList)
                namespacesToImport.extend(fileList)
        #idRe = re.compile('^[\w]+$')
        spells = {}
        provides = {}
        namespacesToImport = list(set(namespacesToImport))
        log.core.debug('Collected namespaces: %s' % str(namespacesToImport))
        log.core.info('Started spells enumerator...')
        for nsToImport in namespacesToImport:
            if not nsToImport in self.forbidden_spells:
                #log.core.info('trying %s...' % nsToImport)
                mod = None
                try:
                    mod = __import__(nsToImport, {}, {}, '*', -1)
                except Exception, e:
                    log.core.warning('Exception while importing %s: %s' % (nsToImport, str(e)))
                    #traceback.print_exc()
                    mod = None

                possibleSpells = []
                plPredicate = lambda x: type(x) == type and issubclass(x, AbstractSpell) and x != AbstractSpell
                possibleSpells = inspect.getmembers(mod, plPredicate)
                if possibleSpells:
                    possibleSpells = map(lambda x: x[1], possibleSpells)
                    for possibleSpell in possibleSpells:
                        instance = possibleSpell()
                        plid = instance.spell_id()
                        #if not idRe.match(plid):
                        #    raise Exception("Incorrect spell Id: %s" % plid)
                        log.core.info("Spell found: %s; base=%s" % (plid, nsToImport))

                        if not spells.has_key(plid):
                            nsName = mod.__name__
                            ns = mod #__import__(nsName, stateVars, {}, '*', -1)
                            instance._set_details(
                                namespace = ns,
                                namespace_name = nsName,
                                file_name = ns.__file__.replace(spellsDir + os.path.sep, '')
                            )
                            spells[plid] = instance
                            prov = instance.provides()
                            if prov:
                                for provId in prov:
                                    if not provId in provides:
                                        provides[provId] = []
                                    provides[provId].append(plid)
                            #log.core.info("Successfully imported: %s; %s; %s" % (ns, nsName, nsToImport))
                        else:
                            log.core.critical("POSSIBLE CONFLICT: Spell with id '%s' already imported!" % plid)
                else:
                    log.core.info('Not a spellspace: %s' % nsToImport)
            else:
                log.core.warning('Namespace ignored due app settings: %s' % nsToImport)

        falseSpells = []
        for provId in provides:
            deps = provides[provId]
            log.core.debug("Functionality '%s' provided by %s" % (provId, alist_to_strlist(deps)))
            newId = "[%s]" % provId
            falseSpell = AbstractSpell(newId, {'info' : 'Dependencies helper for %s' % provId,
                                               'deps' : tuple(deps),
                                              })
            spells[newId] = falseSpell
            falseSpells.append(falseSpell)

        spellsList = spells.values()
        internalSpells = filter(lambda spell: issubclass(type(spell), InternalSpell), spellsList)
        log.core.info("IMPORT STAGE COMPLETED. Imported %d spells (%d provided by Agatsuma, %d fake spells for groups):"
                      % (len(spells), len(internalSpells), len(falseSpells)))
        self.print_spells_list(spellsList)

        log.core.info('RESOLVING DEPENDENCIES...')
        needCheck = True
        while needCheck:
            needCheck = False
            for id in spells.keys():
                deps = spells[id].deps()
                if deps:
                    for dep in deps:
                        if not dep in spells:
                            log.core.warning('[WARNING] Disconnected: "%s"; non-existent dependence: "%s"' % (id, dep))
                            for falseSpell in falseSpells:
                                falseSpell._remove_dep(id)
                            del spells[id]
                            needCheck = True
                            break

        log.core.info('Arranging spells...')
        resolved = []
        needIteration = True
        while needIteration:
            needIteration = False
            for id in spells.keys():
                deps = spells[id].deps()

                ok = True
                if deps:
                    for dep in deps:
                        ok = ok and dep in resolved

                if ok:
                    #if not deps:
                    #    log.core.info('No dependencies for "%s"; adding as %d' % (id, len(self.spells)))
                    #else:
                    #    log.core.info('Already resolved dependencies for "%s"; adding as %d' % (id, len(self.spells)))
                    self.__register_spell(spells[id])
                    resolved.append(id)
                    del spells[id]
                    needIteration = True
                    break
            #log.core.info('new iteration, already resolved: %s' % resolved)

        cyclicDeps = sorted(spells.values(), lambda a, b: cmp(len(a.deps()), len(b.deps())))
        for spell in cyclicDeps:
            log.core.warning('[WARNING] Adding loop-dependant spell "%s" (deps: %s)' % (spell.spell_id(), str(spell.deps())))
            self.__register_spell(spell)

        spellsNames = map(lambda p: p.spell_id(), self.core.spells)
        log.core.debug("Connected %d spells: %s. False spells will be removed now" % (len(spellsNames), str(spellsNames)))

        for spell in falseSpells:
            self.__unregister_spell(spell)

        spellsNames = map(lambda p: p.spell_id(), self.core.spells)
        log.core.info("RESOLVING STAGE COMPLETED. Connected %d spells: %s" % (len(spellsNames), str(spellsNames)))
        log.core.info('SPELLS ENUMERATING COMPLETED')

    def eagerUnload(self):
        log.core.debug("Performing eager unload...")
        toUnload = filter(lambda spell: spell.config.get('eager_unload', None),
                          self.core.spells)
        for spell in toUnload:
            log.core.debug('Eager unloading "%s"' % spell.spell_id())
            self.__unregister_spell(spell)

    def print_spells_list(self, spells):
        for spell in spells:
            log.core.info("* %s, %s, %s" % (spell.spell_id(), spell.namespace_name(), spell.file_name()))
