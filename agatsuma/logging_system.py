# -*- coding: utf-8 -*-

import logging
import multiprocessing

class LoggingSystem(object):
    '''
    Logging sub-system. Just wrapper of python.logging with some start-up configuration.
    '''
    loggersNeedUpdate = {} # TODO: i don't know why it needs. Need to file all occurs and review

    instance = None
    
    def __new__(cls, *a, **kva):
        '''
        Singleton getter/creator
        @param first param: name of logger
        @return: LoggingSystem or logger(if we have argument)
        '''
        if cls.instance is None:
            cls.instance = object.__new__(cls, *a, **kva)
            
        #if we have argument, we need to return logger immediately
        if len(a) == 1:
            return cls.instance.get_logger(a[0])
        return cls.instance

    def __init__(self, level=logging.DEBUG):
        '''
        Some start-up configuration.
        '''
        # TODO: remove this line if it'll be unused
        #formatter = logging.Formatter("[%(asctime)s %(process)d:%(thread)d:%(name)s:%(levelname)s] %(message)s")
        logging.basicConfig(
            level = level,
            format = "[%(asctime)s %(name)s:%(levelname)s] %(message)s")
        self.get_logger("logging").debug("online!")
    
    def __getattr__(self, name):
        '''
        I want to make this class so easy and transparent in relation to logging module.
        Perhaps, its dirty, but easy.
        I want make this class access directly to logger via getattr w/o creating inner container of loggers.
        '''
        if hasattr(self, name):
            if name == "get_logger":
                return self.get_logger
            elif name == "instance":
                return self.instance
            elif name == "__call__":
                return self.__call__
            elif name == "__new__":
                return self.__new__
            elif name == "configure":
                return self.configure
            elif name == "__init__":
                return self.__init__
        else:
            return self.get_logger(name)
        
    def __call__(self, name):
        '''
        Shortcut for get_logger
        '''
        return self.instance.get_logger(name)
    
    def get_logger(self, name):
        '''
        Just wrapper for future hooks
        @param name: name of logger
        @return: logger
        '''
        return logging.getLogger(name)
    
    def configure(self, config):
        '''
        Configure loggers by configuration dictionary
        @param config: dict of logger configuration (see http://docs.python.org/library/logging.html#logging.dictConfig)
        '''
        raise Exception("Not implemented yet")