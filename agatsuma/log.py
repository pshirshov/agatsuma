# -*- coding: utf-8 -*-

import logging
import multiprocessing

class log(object):
    loggers = {}
    rootHandler = None

    def initiateLoggers(self):
        formatter = logging.Formatter("[%(asctime)s %(name)s:%(levelname)s] %(message)s")
        #logQueue = multiprocessing.Queue(100)
        #log.rootHandler = MultiProcessingLogHandler(logging.StreamHandler(), logQueue)
        log.rootHandler = logging.StreamHandler()
        log.rootHandler.setLevel(logging.DEBUG) # TODO:
        log.rootHandler.setFormatter(formatter)
        logging.getLogger('').addHandler(log.rootHandler)
    
    @staticmethod
    def newLogger(loggerName, loggingLevel, handler = None):
        assert loggerName in log.loggers or (getattr(log, loggerName, None) is None)
        if loggerName in log.loggers:
            return log.loggers[loggerName]
        logger = logging.getLogger(loggerName)
        logger.setLevel(loggingLevel)
        log.loggers[loggerName] = logger
        setattr(log, loggerName, logger)
        if handler:
            logger.addHandler(handler)
        logger.debug("Logger registered")
        return logger       
        
    def updateLevels(self):
        from agatsuma.settings import Settings
        if Settings.core.debug:
            if Settings.core.debug_level > 1:
                logger = multiprocessing.log_to_stderr()
                logger.setLevel(logging.DEBUG)
            log.rootHandler.setLevel(logging.DEBUG)
        else:
            log.rootHandler.setLevel(logging.INFO)    
