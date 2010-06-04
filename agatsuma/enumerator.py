# -*- coding: utf-8 -*-

import sys
import os
import inspect

from agatsuma.log import log
from agatsuma.interfaces.abstract_spell import AbstractSpell

class Enumerator(object):
    def __init__(self, core, appDir):
        self.appDir = appDir
        self.prohibitedSpells = [] # TODO: config
        self.core = core
        #def appBaseName(self):
        #  return self.__module__.split('.')[0]

    def registerSpell(self, spell):
        self.core.spells.append(spell)
        self.core.spellsDict[spell.spellId()] = spell

    def enumerateSpells(self, essentialSpellSpaces):
        spellsDir = self.appDir #os.path.realpath(os.path.join(self.OPT.appPath, 'controllers'))
        basicNamespace = os.path.basename(spellsDir)
        if not self.core.appName:
            self.core.appName = basicNamespace[0].capitalize() + basicNamespace[1:]
        #sys.path.append(spellsDir)
        log.core.debug("System paths:")
        for p in sys.path:
            log.core.debug("* %s" % p)    
            
        log.core.info("Collecting names of possible spells...")
        log.core.info("Spells root directory: %s" % spellsDir)
        log.core.info("Spells namespace: %s" % basicNamespace)

        namespacesToImport = []
        namespacesToImport.extend(essentialSpellSpaces)
        for root, dirs, files in os.walk(spellsDir):
            def useFilePred(file):
                if file in self.prohibitedSpells:
                    log.core.warning('File ignored due config settings: %s' % file)
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

        spells = {}
        print namespacesToImport
        log.core.info('Started spells enumerator...')
        for nsToImport in namespacesToImport:
            if not nsToImport in self.prohibitedSpells:
                #log.core.info('trying %s...' % nsToImport)
                mod = None
                try:
                    mod = __import__(nsToImport, fromlist = '*')
                except Exception, e:
                    log.core.warning('Exception while importing %s: %s' % (nsToImport, str(e)))
                    mod = None

                possibleSpells = []
                plPredicate = lambda x: type(x) == type and issubclass(x, AbstractSpell) and x != AbstractSpell
                possibleSpells = inspect.getmembers(mod, plPredicate)
                if possibleSpells:
                    possibleSpells = map(lambda x: x[1], possibleSpells)

                if possibleSpells:
                    for possibleSpell in possibleSpells:
                        instance = possibleSpell()
                        plid = instance.spellId()
                        log.core.info("Importing spell: %s; base=%s" % (plid, nsToImport))

                        if not spells.has_key(plid):
                            #nsName = basicNamespace + mod.__name__
                            nsName = mod.__name__
                            ns = __import__(nsName, {}, {}, '*', -1)
                            instance.setDetails(
                                namespace = ns,
                                namespaceName = nsName,
                                fileName = ns.__file__.replace(spellsDir + os.path.sep, '')
                            )
                            spells[plid] = instance
                            #log.core.info("Successfully imported: %s; %s; %s" % (ns, nsName, nsToImport))
                        else:
                            log.core.critical("POSSIBLE CONFLICT: Spell with id '%s' already imported!" % plid)
                else:
                    log.core.info('Not a spellspace: %s' % nsToImport)
            else:
                log.core.warning('Namespace ignored due config settings: %s' % nsToImport)

        log.core.info("IMPORT STAGE COMPLETED. Imported %d spells:" % len(spells))
        for spell in spells.values():
            log.core.info("* %s, %s, %s" % (spell.spellId(), spell.namespaceName(), spell.fileName()))
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
                            del spells[id]
                            needCheck = True
                            break

        log.core.info('Arranging spells...')
        resolved = []
        needIteration = True
        while needIteration:
            needIteration = False
            for id in spells.keys():
                #log.core.info('testing: ' + id)
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
                    self.registerSpell(spells[id])
                    resolved.append(id)
                    del spells[id]
                    needIteration = True
                    break
            #log.core.info('new iteration, already resolved: %s' % resolved)

        cyclicDeps = sorted(spells.values(), lambda a, b: cmp(len(a.deps()), len(b.deps())))
        for spell in cyclicDeps:
            log.core.warning('[WARNING] Adding loop-dependant spell "%s" (deps: %s)' % (spell.spellId(), str(spell.deps())))
            self.registerSpell(spell)

        spellsNames = map(lambda p: p.spellId(), self.core.spells)
        log.core.info("RESOLVING STAGE COMPLETED. Connected %d spells: %s" % (len(spellsNames), str(spellsNames)))
        log.core.info('SPELLS ENUMERATING COMPLETED')     
