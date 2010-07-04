# -*- coding: utf-8 -*-

class EAbstractFunctionCall(Exception):
    def __repr__(self):
        return "Call to abstract function"
