# -*- coding: utf-8 -*-

import json

import datetime
import multiprocessing

from agatsuma import log
from agatsuma.interfaces import AbstractSpell

class DictAccessProxy(object):
    def __init__(self, groupName, sourceDict, roList, types, comments):
        object.__setattr__(self, '_DictAccessProxy__dict', sourceDict)
        self.__roList = roList
        self.__groupName = groupName
        self.__types = types
        self.__comments = comments

    def __getattr__(self, name):
        storedDict = object.__getattribute__(self, '_DictAccessProxy__dict')
        if name in storedDict:
            return storedDict[name]
        else:
            return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in self.__dict:
            if name in self.__roList:
                raise Exception("Option '%s.%s' is read-only" % (self.__groupName, name))
            elif type(value) != self.__types[name]:
                raise Exception("Option '%s.%s' must have type %s, but %s tried to assign" % 
                                (self.__groupName, 
                                 name, 
                                 self.__types[name], 
                                 type(value),
                                )
                               )
            else:
                self.__dict[name] = value
                Settings.setConfigData(Settings.settings)
        else:
            object.__setattr__(self, name, value)

    def __repr__(self):
        return str("<Settings group: %s>" % self.__dict)

class SettingsMeta(type):
    def __setattr__(stype, name, value):
       if name in type.__getattribute__(stype, "settings"):
           raise Exception("It's not allowed to overwrite settings group")
       else:
           type.__setattr__(stype, name, value)

    def __getattribute__(stype, name):
        settings = type.__getattribute__(stype, "settings")
        if name in settings:
            return DictAccessProxy(name, # group
                                   settings[name], 
                                   Settings.roSettings[name], 
                                   Settings.types[name],
                                   Settings.comments[name])
        else:
            return type.__getattribute__(stype, name)

class Settings(object):
    __metaclass__ = SettingsMeta
    settings = {}
    roSettings = []
    types = {}
    recovery = False
    
    def __setattr__(self, name, value):
        if name in type.__getattribute__(Settings, "settings"):
            raise Exception("It's now allowed to overwrite settings group")
        else:
            object.__setattr__(self, name, value)

    def __getattr__(self, name):
        settings = type.__getattribute__(Settings, "settings")
        if name in settings:
            return DictAccessProxy(name, # group
                                   settings[name], 
                                   Settings.roSettings[name], 
                                   Settings.types[name],
                                   Settings.comments[name])
        else:
            return object.__getattribute__(self, name)
    
    def __init__(self, config, descriptors, **kwargs):
        conf = open(config, 'r')
        settings = conf.read()
        Settings.recovery = kwargs.get('recovery', False)
        conf.close()
        log.core.info("Loading config '%s'" % config)
        self.parseSettings(settings, descriptors)
        log.core.info('Config loaded')
    
    def parseSettings(self, settings, descriptors):
        settings = self.load(settings)
        problems = []
        newsettings = {}
        rosettings = {}
        types = {}
        comments = {}
        actual = 0
        rocount = 0
        for group, name, ro, stype, comment in descriptors.values():
            if not group in settings:
                problems.append("Group '%s' (%s) not found in settings" % 
                                (group, comment))
                continue
            groupDict = settings[group]
            if not name in groupDict:
                problems.append("Setting '%s' (%s) not found in group '%s'" % 
                                (name, comment, group))
                continue
            value = groupDict[name]
            rstype = type(value)
            #if stype == str and type(value) == unicode:
            #    rstype = unicode
            #    value = str(value)
            fullname = '%s.%s' % (group, name)
            if rstype != stype:
                problems.append("Setting '%s' (%s) has incorrect type '%s' instead of '%s'" % 
                                (fullname, comment, str(rstype), str(stype)))
                continue
            
            if not group in newsettings:
                newsettings[group] = {}
                types[group] = {}
                comments[group] = {}
                rosettings[group] = []
            newsettings[group][name] = value
            types[group][name] = stype
            comments[group][name] = comment
            if ro:
                rosettings[group].append(name)
                rocount += 1
            actual += 1
        if problems:
            log.core.error('\n'.join(problems))
            raise Exception("Can't load settings")
        log.core.info('%d settings found in config, %d are actual (%d read-only)' % (len(descriptors), actual, rocount))
        Settings.roSettings = rosettings
        Settings.types = types
        Settings.comments = comments
        Settings.descriptors = descriptors
        Settings.setConfigData(newsettings)

    @staticmethod
    def setConfigData(settings, **kwargs):
        from agatsuma.core import Core
        process = multiprocessing.current_process()
        log.core.info("Installing new config data in process '%s' with PID %d" % (str(process.name), process.pid))
        timestamp = datetime.datetime.now()
        Settings.settings.update(settings)
        if settings["core"]["debug_level"] > 0:
            log.core.debug("Updated config: %s" % str(Settings.settings))
        Settings.configData = {"data": settings,
                               "update" : timestamp,
                              }
        spells = Core.instance._implementationsOf(AbstractSpell)
        for spell in spells:
            spell.postConfigUpdate(**kwargs)

    def load(self, settings):
        """
        Should return json-like dictionary of settings
        """
        return json.loads(settings)
    
    def dump(self):
        return json.dumps(Settings.settings)
