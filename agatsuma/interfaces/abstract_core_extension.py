# -*- coding: utf-8 -*-

from agatsuma.errors import EAbstractFunctionCall

class AbstractCoreExtension(object):
    def init(self, core, appDirs, appConfig, kwargs):
        return (appDirs, appConfig, kwargs)

    @staticmethod
    def name():
        raise EAbstractFunctionCall()

    def additional_methods(self):
        return []

    def on_core_post_configure(self, core):
        pass

    def on_core_stop(self, core):
        pass
