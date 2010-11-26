# -*- coding: utf-8 -*-
import re

from agatsuma.core import Core

class Url(object):
    """
    """
    def __init__(self, name, string, handler):
        """
        """
        self.name = name
        self.handler = handler
        self.__string = string
        self.regex = self.__regex()
        self.template = self.__template()

    def __regex(self):
        # TODO: more complex logic
        rex = re.compile(r'%\((\w+)\)(\w)') 
        def replacer(obj):
            t = obj.group(2)
            if t == 'd':
                return r'(\d+)'
            elif t == 's':
                return r'(\w+)'
        return rex.sub(replacer, self.__string)

    def __template(self):
        return self.__string

class UrlFor(object):
    """Url Generator
    """
    def __init__(self, name, **kwargs):
        """
        Arguments:
        - `name`:
        """
        self._name = name
        self._kwargs = kwargs

    def __str__(self):
        return Core.instance.URITemplates[self._name] % self._kwargs
