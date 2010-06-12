# -*- coding: utf-8 -*-

class SettingsBackend(object):
    def get(self, name, currentValue):
      return currentValue
     
    def save(self, name, value):
        pass