import logging

class MPLogHandler(logging.Handler):
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

"""
# Another MP idea:
#http://stackoverflow.com/questions/641420/how-should-i-log-while-using-multiprocessing-in-python
"""
