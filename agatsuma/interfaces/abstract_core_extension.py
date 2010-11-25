# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

#from agatsuma.errors import EAbstractFunctionCall

class MyMeta(ABCMeta):
    def __new__(a, b, c, d):
        print a, "//", b, "//", c, "//", d
        print type(d), dir(d), d
        return ABCMeta.__new__(a, b, c, d)

def zzz(f):
    print ">>>", f, type(f)
    #f.zhopa = True
    #setattr(f, "zhopa", True)
    return f
    #raise Exception("!!!")
    def zhopa(*args, **kwargs):
        print "HERE"
        raise Exception("OLOLOL")
        return f(*args, **kwargs)
    #return zhopa

class AbstractCoreExtension(object):
    __metaclass__ = MyMeta

    def init(self, core, app_directorys, appConfig, kwargs):
        return (app_directorys, appConfig, kwargs)

    @zzz
    @staticmethod
    def name():
        print "OLOLO"
        return None
        raise EAbstractFunctionCall()

    @classmethod
    def __subclasshook__(cls, C):
        print cls, C
        
    #@abstractmethod
    def additional_methods(self):
        return []

    def on_core_post_configure(self, core):
        pass

    def on_core_stop(self, core):
        pass

class Z(AbstractCoreExtension):
    #pass
    @staticmethod
    def name():
        return None

print 'begin'
a = AbstractCoreExtension()
print a.name()
z = Z()
print z.name()
print z

