# -*- coding: utf-8 -*-
import collections

"""
    Inspired by
    http://github.com/milancermak/tornado/blob/master/tornado/session.py
"""

class AbstractSession(collections.MutableMapping):
    def __init__(self, sess_id, data): #, manager, handler):
        self.id = sess_id
        self.data = data
        self.handler = None
        self.sessman = None
        self.saved = False
        self.cookieSent = False

    def fill(self, ip, user_agent):
        self.data["ip"] = ip
        self.data["user_agent"] = user_agent

    def __repr__(self):
        return '<session id: %s data: %s>' % (self.id, self.data)

    def __str__(self):
        return "sess_%s" % self.id

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.modified = True

    def __delitem__(self, key):
        del self.data[key]
        self.modified = True

    def keys(self):
        return self.data.keys()

    def __iter__(self):
        return self.data.__iter__()

    def __len__(self):
        return len(self.data.keys())

    def save(self):
        self.sessSpell.save_session(self)

    def delete(self):
        self.sessSpell.delete_session(self)
