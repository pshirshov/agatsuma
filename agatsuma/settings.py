# -*- coding: utf-8 -*-

import json
import datetime
import multiprocessing

from agatsuma.log import log

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
                #print "correct assignment"
                # TODO: signals about change && updates
        else:
            object.__setattr__(self, name, value)

    def __repr__(self):
        return str("<Settings group: %s>" % self.__dict)

class SettingsMeta(type):
    def __setattr__(stype, name, value):
       #print "@__set__", stype, name, value
       if name in type.__getattribute__(stype, "settings"):
           raise Exception("It's not allowed to overwrite settings group")
       else:
           type.__setattr__(stype, name, value)

    def __getattribute__(stype, name):
        #print "@__get__", stype, name
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
    
    def __init__(self, config, descriptors):
        conf = open(config, 'r')
        settings = conf.read()
        conf.close()
        log.core.info("Loading config '%s'" % config)
        self.parseSettings(settings, descriptors)
        log.core.info('Config loaded')
    
    def parseSettings(self, settings, descriptors):
        settings = json.loads(settings)
        problems = []
        newsettings = {}
        rosettings = {}
        types = {}
        comments = {}
        actual = 0
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
                
            actual += 1
        if problems:
            log.core.error('\n'.join(problems))
            raise Exception("Can't load settings")
        log.core.info('%d settings found in config, %d are actual (%d read-only)' % (len(descriptors), actual, len(rosettings)))
        #Settings.settings = newsettings
        Settings.roSettings = rosettings
        Settings.types = types
        Settings.comments = comments
        Settings.descriptors = descriptors
        Settings.setConfigData(newsettings) #Settings.settings)

    @staticmethod
    def setConfigData(settings, updateShared = True):#, timestamp = None):
        from agatsuma.core import Core
        #print settings
        #print type(settings)
        #if not timestamp:
        log.core.info("Installing new config data in thread %s" % str(multiprocessing.current_process()))
        timestamp = datetime.datetime.now()
        Settings.settings.update(settings)
        Settings.configData = {"data": settings,
                               "update" : timestamp,
                              }
        if updateShared:
            log.core.info("Propagating new config data to workers")
            Core.sharedConfigData.update(Settings.configData)

    @staticmethod
    def dump():
        return json.dumps(Settings.settings)

    def __setattr__(self, name, value):
        #print "__set__", name, value
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


