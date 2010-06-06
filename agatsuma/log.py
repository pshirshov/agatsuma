# -*- coding: utf-8 -*-

import logging
import time
#import multiprocessing
#import tornado.ioloop

class MPQueueHandler(logging.Handler):
    def __init__(self, queue, handler):
        logging.Handler.__init__(self)
        self.queue = queue
        self.realHandler = handler

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self.realHandler.setFormatter(fmt)
        
    def _format_record(self, record):
        ei = record.exc_info
        if ei:
            dummy = self.format(record) # just to get traceback text into record.exc_text
            record.exc_info = None  # to avoid Unpickleable error
        return record

    def send(self, s):
        self.queue.put(s)

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        #except (KeyboardInterrupt, SystemExit): # is it needed ?
        #    raise
        except:
            self.handleError(record)
    
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
    """
    def setMPHandler(self, ioloop):
        from agatsuma.settings import Settings
        pumpTimeout = Settings.core.logger_pump_timeout
        self.logQueue = MPQueue()
        self.logPump = tornado.ioloop.PeriodicCallback(self.processLog, pumpTimeout, io_loop=ioloop)
        log.rootHandler = MPQueueHandler(self.logQueue, log.rootHandler)
        self.logPump.start()
    """
    
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

"""
import threading
import Queue

#http://stackoverflow.com/questions/641420/how-should-i-log-while-using-multiprocessing-in-python
class MultiProcessingLogHandler(logging.Handler):
    def __init__(self, handler, queue, child=False):
        logging.Handler.__init__(self)

        self._handler = handler
        self.queue = queue

        # we only want one of the loggers to be pulling from the queue.
        # If there is a way to do this without needing to be passed this
        # information, that would be great!
        if child == False:
            self.shutdown = False
            self.polltime = 1
            t = threading.Thread(target=self.receive)
            t.daemon = True
            t.start()

    def setFormatter(self, fmt):
        logging.Handler.setFormatter(self, fmt)
        self._handler.setFormatter(fmt)
        
    def _format_record(self, record):
        ei = record.exc_info
        if ei:
            dummy = self.format(record) # just to get traceback text into record.exc_text
            record.exc_info = None  # to avoid Unpickleable error
        return record

    def receive(self):
        #print "receive on"
        while (self.shutdown == False) or (self.queue.empty() == False):
            # so we block for a short period of time so that we can
            # check for the shutdown cases.
            try:
                record = self.queue.get(True, self.polltime)
                self._handler.emit(record)
            except Queue.Empty, e:
                pass

    def send(self, s):
        # send just puts it in the queue for the server to retrieve
        self.queue.put(s)

    def emit(self, record):
        try:
            s = self._format_record(record)
            self.send(s)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        time.sleep(self.polltime+1) # give some time for messages to enter the queue.
        self.shutdown = True
        time.sleep(self.polltime+1) # give some time for the server to time out and see the shutdown

    def __del__(self):
        self.close() # hopefully this aids in orderly shutdown when things are going poorly.
"""
