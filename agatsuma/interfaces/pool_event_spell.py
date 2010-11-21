# -*- coding: utf-8 -*-

class IPoolEventSpell(object):
    """
    Implementations of this mix-in interface may react events related to
    process pool created by :class:`agatsuma.core.MPCore`.
    """

    def pre_pool_init(self, core):
        """ Multiprocessing core calls this method just before
        initialization of processes pool
        (and after all
        :meth:`agatsuma.interfaces.AbstractSpell.post_configure`
        calls).

        So this method may be used to initialize some objects that should be
        copied to all the worker processes.
        """
        pass

    def post_pool_init(self, core):
        """ Multiprocessing core calls this method recently after
        initialization of processes pool.

        So this method may be used to initialize some objects
        that should be unique for main process.
        """
        pass
