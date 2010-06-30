# -*- coding: utf-8 -*-

import logging

class FidelityWorker(object):
    functions = {}
    def __init__(self, worker):
        self.workerId = id(worker)
        self.workerName = worker.__name__
        FidelityWorker.functions[self.workerId] = worker

    def __call__(self, *args, **kwargs):
        try:
            return FidelityWorker.functions[self.workerId](*args, **kwargs)
        except Exception:
            logging.error("Exception in MP worker", exc_info=True)

