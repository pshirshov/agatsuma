# -*- coding: utf-8 -*-

class PoolEventSpell(object):
    """
    Implementations of this mix-in interface may react events related to
    process pool created by :class:`agatsuma.core.MPCore`.
    """

    def prePoolInit(self, core):
        """ Multiprocessing core calls this method just before
        initialization of processes pool
        (and after all
        :meth:`agatsuma.interfaces.AbstractSpell.postConfigure`
        calls).

        So this method may be used to initialize some objects that should be
        copied to all the worker processes.
        """
        pass

    def postPoolInit(self, core):
        """ Multiprocessing core calls this method recently after
        initialization of processes pool.

        So this method may be used to initialize some objects
        that should be unique for main process.
        """
        pass
