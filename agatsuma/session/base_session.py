# -*- coding: utf-8 -*-
try:
    import cPickle as pickle
except:
    import pickle

import base64
import collections
import datetime
import os
#import time

"""
import csv
import re
import tempfile
import types
"""

"""
    Inspired by 
    http://github.com/milancermak/tornado/blob/master/tornado/session.py
"""



class Session(collections.MutableMapping):
    def __init__(self, sess_id, data): #, manager, handler):
        self.id = sess_id
        self.data = data
        self.data["timestamp"] = datetime.datetime.now() 
        #self.manager = manager
        self.handler = None
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
        
    """
    def save(self):
        self.manager.save(self)

    def delete(self):
        self.manager.delete(self)
    """
    
class BaseSessionIdea(collections.MutableMapping):
    """The base class for the session object. Work with the session object
is really simple, just treat is as any other dictionary:

class Handler(tornado.web.RequestHandler):
def get(self):
var = self.session['key']
self.session['another_key'] = 'value'

Session is automatically saved on handler finish. Session expiration
is updated with every request. If configured, session ID is
regenerated periodically.

The session_id attribute stores a unique, random, 64 characters long
string serving as an indentifier.

To create a new storage system for the sessions, subclass BaseSession
and define save(), load() and delete(). For inspiration, check out any
of the already available classes and documentation to aformentioned functions."""
    def __init__(self, 
                 session_id=None, 
                 data=None,  
                 expires=None,
                 duration=None, 
                 ip_address=None,
                 user_agent=None,
                 regeneration_interval=None, 
                 next_regeneration=None, 
                 **kwargs):
        # if session_id is True, we're loading a previously initialized session
        if session_id:
            self.session_id = session_id
            self.data = data
            self.duration = duration
            self.expires = expires
            self.dirty = False
        else:
            self.session_id = self._generate_session_id()
            self.data = {}
            self.duration = duration
            self.expires = self._expires_at()
            self.dirty = True

        self.ip_address = ip_address
        self.user_agent = user_agent
        self.regeneration_interval = regeneration_interval
        self.next_regeneration = next_regeneration or self._next_regeneration_at()
        self._delete_cookie = False

    def __repr__(self):
        return '<session id: %s data: %s>' % (self.session_id, self.data)

    def __str__(self):
        return self.session_id

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
        self.dirty = True

    def __delitem__(self, key):
        del self.data[key]
        self.dirty = True

    def keys(self):
        return self.data.keys()

    def __iter__(self):
        return self.data.__iter__()

    def __len__(self):
        return len(self.data.keys())

    def _generate_session_id(cls):
        return os.urandom(32).encode('hex') # 256 bits of entropy

    def _is_expired(self):
        """Check if the session has expired."""
        return datetime.datetime.now() > self.expires

    def _expires_at(self):
        """Find out the expiration time. Returns datetime.datetime."""
        v = self.duration
        if isinstance(v, datetime.timedelta):
            pass
        elif isinstance(v, (int, long)):
            self.duration = datetime.timedelta(seconds=v)
        elif isinstance(v, basestring):
            self.duration = datetime.timedelta(seconds=int(v))
        else:
            self.duration = datetime.timedelta(seconds=900) # 15 mins

        return datetime.datetime.now() + self.duration

    def _should_regenerate(self):
        return datetime.datetime.now() > self.next_regeneration

    def _next_regeneration_at(self):
        v = self.regeneration_interval
        if isinstance(v, datetime.timedelta):
            pass
        elif isinstance(v, (int, long)):
            self.regeneration_interval = datetime.timedelta(seconds=v)
        elif isinstance(v, basestring):
            self.regeneration_interval = datetime.timedelta(seconds=int(v))
        else:
            self.regeneration_interval = datetime.timedelta(seconds=240) # 4 mins

        return datetime.datetime.now() + self.regeneration_interval

    def invalidate(self):
        self.delete() # remove server-side
        self._delete_cookie = True # remove client-side
    
    def refresh(self, duration=None, new_session_id=False):
        if duration:
            self.duration = duration
            self.expires = self._expires_at()
        else:
            self.expires = self._expires_at()
        if new_session_id:
            self.delete()
            self.session_id = self._generate_session_id()
            self.next_regeneration = self._next_regeneration_at()
        self.dirty = True # force save
        self.save()

    def serialize(self):
        dump = {'session_id': self.session_id,
                'data': self.data,
                'duration': self.duration,
                'expires': self.expires,
                'ip_address': self.ip_address,
                'user_agent': self.user_agent,
                'security_model': self.security_model,
                'regeneration_interval': self.regeneration_interval,
                'next_regeneration': self.next_regeneration}
        return base64.encodestring(pickle.dumps(dump))

    @staticmethod
    def deserialize(datastring):
        return pickle.loads(base64.decodestring(datastring))
        
    def save(self):
        """Save the session data and metadata to the backend storage
if necessary (self.dirty == True). On successful save set
dirty to False."""
        pass

    @staticmethod
    def load(session_id, location):
        """Load the stored session from storage backend or return
None if the session was not found, in case of stale cookie."""
        pass

    def delete(self):
        """Remove all data representing the session from backend storage."""
        pass

    @staticmethod
    def delete_expired(file_path):
        """Deletes sessions with timestamps in the past form storage."""
        pass