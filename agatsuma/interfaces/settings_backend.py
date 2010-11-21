# -*- coding: utf-8 -*-

class AbstractSettingsBackend(object):
    def get(self, name, currentValue):
      return currentValue
     
    def save(self, name, value):
        pass