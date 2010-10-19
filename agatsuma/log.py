# -*- coding: utf-8 -*-

import logging
import multiprocessing

class log(object):
    loggers = {}
    rootHandler = None
    loggersNeedUpdate = {}

    def initiate_loggers(self):
        #formatter = logging.Formatter("[%(asctime)s %(process)d:%(thread)d:%(name)s:%(levelname)s] %(message)s")
        formatter = logging.Formatter("[%(asctime)s %(name)s:%(levelname)s] %(message)s")
        log.rootHandler = logging.StreamHandler()
        log.rootHandler.setLevel(logging.DEBUG) # TODO:
        log.rootHandler.setFormatter(formatter)
        logging.getLogger('').addHandler(log.rootHandler)

    @staticmethod
    def new_logger(loggerName, **kwargs):
        assert loggerName in log.loggers or (getattr(log, loggerName, None) is None)
        handler = kwargs.get('handler', None)
        #level = kwargs.get('level', None)
        if loggerName in log.loggers:
            return log.loggers[loggerName]
        logger = logging.getLogger(loggerName)
        #if not level:
        level = logging.DEBUG # TODO:
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
    def __str_to_level(s):
        return log.__levels[s]

    def update_levels(self):
        from agatsuma.settings import Settings
        defaultLevel = log.__str_to_level(Settings.logging.default_level)
        rootLevel = log.__str_to_level(Settings.logging.root_level)
        log.rootHandler.setLevel(rootLevel)

        levels = Settings.logging.levels
        #formatters = Settings.logging.formatters
        for loggerName, logger in log.loggers.items():
            level = levels.get(loggerName, None)
            if level:
                level = log.__str_to_level(level)
            else:
                level = defaultLevel
            log.core.debug("Setting level for logger '%s' to %d" %
                           (loggerName, level))
            logger.setLevel(level)
            #formatter = formatters.get(loggerName, None)
            #print dir(logger)
            #if formatter:
            #    log.core.debug("Setting formatter for logger '%s' to %s" %
            #               (loggerName, formatter))

        namedLevels = Settings.logging.named_levels
        for loggerName, level in namedLevels.items():
            namedLog = logging.getLogger(loggerName)
            namedLog.setLevel(log.__str_to_level(level))

        # TODO: maybe move it into config?
        if Settings.core.debug:
            if Settings.core.debug_level > 1:
                logger = multiprocessing.log_to_stderr()
                logger.setLevel(logging.DEBUG)
