# -*- coding: utf-8 -*-
import datetime
try:
    import cPickle as pickle
except:
    import pickle

import base64
import re

from agatsuma.core import Core
from agatsuma.settings import Settings
from agatsuma.log import log
from agatsuma.interfaces import AbstractSpell, RequestSpell
#from agatsuma.session.base_session_manager import DummySessionManager

class SessionSpell(AbstractSpell, RequestSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Session Spell',
                  'deps' : ()
                 }
        AbstractSpell.__init__(self, 'agatsuma_session', config)
        
    def preConfigure(self, core):
        import logging
        log.newLogger("sessions", logging.DEBUG)
        core.registerOption("!sessions.storage_uri", unicode, "Storage URI")
        core.registerOption("!sessions.expiration_interval", int, "Default session length in seconds")

    def postConfigure(self, core):
        log.core.info("Initializing Session Storage..")
        # TODO: get settings and open connection in children
        rex = re.compile(r"^(\w+)\+(.*)$")
        match = rex.match(Settings.sessions.storage_uri)
        if match:
            managerId = match.group(1)
            uri = match.group(2)
            spellName = "tornado_session_backend_%s" % managerId
            spell = Core.instance.spellsDict[spellName]
            self.sessman = spell.instantiateBackend(uri)
        else:
            raise Exception("Incorrect session storage URI")
        #self.sessman = DummySessionManager() # TODO: select appropriate session class
        
    def beforeRequestCallback(self, handler):
        # TODO: on-demand loading strategy
        cookie = handler.get_secure_cookie("AgatsumaSessId")
        print "COOKIE>", cookie
        session = None
        if cookie:
            session = self.sessman.load(cookie)
            if session:
                print "here"
                session.handler = handler
                # Update timestamp if left time < than spent time
                timestamp = session["timestamp"]
                now = datetime.datetime.now() 
                print "spent", (now - timestamp)
                print "left", (self.sessman.sessionDoomsday(timestamp)- now)
                if (now - timestamp) >= (self.sessman.sessionDoomsday(timestamp)- now):
                    print "Updating session's timestamp"
                    self.sessman.save(session)
        if not session:
            session = self.sessman.new(handler.request.remote_ip, 
                                       handler.request.headers["User-Agent"])
            session.handler = handler
            self.sessman.save(session)
        handler.session = session
        session.sessman = self.sessman
                    