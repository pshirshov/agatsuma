# -*- coding: utf-8 -*-

import logging
import multiprocessing

class log(object):
    loggers = {}
    rootHandler = None
    loggersNeedUpdate = {}
    
    def initiateLoggers(self):
        formatter = logging.Formatter("[%(asctime)s %(name)s:%(levelname)s] %(message)s")
        #logQueue = multiprocessing.Queue(100)
        #log.rootHandler = MultiProcessingLogHandler(logging.StreamHandler(), logQueue)
        log.rootHandler = logging.StreamHandler()
        log.rootHandler.setLevel(logging.DEBUG) # TODO:
        log.rootHandler.setFormatter(formatter)
        logging.getLogger('').addHandler(log.rootHandler)

    @staticmethod
    def newLogger(loggerName, **kwargs):
        assert loggerName in log.loggers or (getattr(log, loggerName, None) is None)
        handler = kwargs.get('handler', None)
        #level = kwargs.get('level', None)
        #autolevel = kwargs.get('autolevel', True)
        #if autolevel and level:
        #    raise Exception("Autolevel cant' be used with custom level")
        if loggerName in log.loggers:
            return log.loggers[loggerName]
        logger = logging.getLogger(loggerName)
        #if not level:
        level = logging.DEBUG
        #if autolevel:
        #    log.loggersNeedUpdate[loggerName] = logger
        logger.setLevel(level)
        log.loggers[loggerName] = logger
        setattr(log, loggerName, logger)
        if handler:
            logger.addHandler(handler)
        logger.debug("Logger registered")
        return logger

    __levels = {'debug'   : logging.DEBUG,
                'info'    : logging.INFO,
                'warning' : logging.WARNING,
                'error'   : logging.ERROR,
                'critical': logging.CRITICAL,
                'notset'  : logging.NOTSET,
        }

    @staticmethod
    def __strToLevel(s):
        return log.__levels[s]

    def updateLevels(self):
        from agatsuma.settings import Settings
        defaultLevel = log.__strToLevel(Settings.logging.default_level)
        rootLevel = log.__strToLevel(Settings.logging.root_level)
        log.rootHandler.setLevel(rootLevel)

        levels = Settings.logging.levels
        for loggerName, logger in log.loggers.items():
            level = levels.get(loggerName, None)
            if level:
                level = log.__strToLevel(level)
            else:
                level = defaultLevel
            log.core.debug("Setting logging level for logger '%s' to %d" %
                           (loggerName, level))
            logger.setLevel(level)

        # TODO: maybe move it into config?
        if Settings.core.debug:
            if Settings.core.debug_level > 1:
                logger = multiprocessing.log_to_stderr()
                logger.setLevel(logging.DEBUG)
