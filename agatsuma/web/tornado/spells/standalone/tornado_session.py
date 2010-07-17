# -*- coding: utf-8 -*-
import datetime
import re

from agatsuma import Spell
from agatsuma import Settings
from agatsuma import log
from agatsuma.interfaces import AbstractSpell, InternalSpell
from agatsuma.web.tornado.interfaces import RequestSpell, SessionHandler

class SessionSpell(AbstractSpell, InternalSpell, RequestSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Session Spell',
                  'deps' : ('agatsuma_tornado', ),
                  'requires' : ('session_backend', ),
                 }
        AbstractSpell.__init__(self, 'agatsuma_session', config)

    def preConfigure(self, core):
        log.newLogger("sessions")
        core.registerOption("!sessions.storage_uri", unicode, "Storage URI")
        core.registerOption("!sessions.expiration_interval", int, "Default session length in seconds")

    def postConfigure(self, core):
        log.sessions.info("Initializing Session Storage..")
        rex = re.compile(r"^(\w+)\+(.*)$")
        match = rex.match(Settings.sessions.storage_uri)
        if match:
            managerId = match.group(1)
            uri = match.group(2)
            spellName = "tornado_session_backend_%s" % managerId
            spell = Spell(spellName)
            if spell:
                self.sessman = spell.instantiateBackend(uri)
            else:
                raise Exception("Session backend improperly configured, spell '%s' not found" % spellName)
        else:
            raise Exception("Incorrect session storage URI")

    def beforeRequestCallback(self, handler):
        if isinstance(handler, SessionHandler):
            cookie = handler.get_secure_cookie("AgatsumaSessId")
            log.sessions.debug("Loading session for %s" % cookie)
            session = None
            if cookie:
                session = self.sessman.load(cookie)
                if session:
                    session.handler = handler
                    # Update timestamp if left time < than elapsed time
                    timestamp = session["timestamp"]
                    now = datetime.datetime.now()
                    elapsed = now - timestamp
                    left = (self.sessman._sessionDoomsday(timestamp)- now)
                    if elapsed >= left:
                        log.sessions.debug("Updating timestamp for session %s (E: %s, L: %s)" % (cookie, str(elapsed), str(left)))
                        self.sessman.save(session)
            if not session:
                session = self.sessman.new(handler.request.remote_ip,
                                           handler.request.headers["User-Agent"])
                session.handler = handler
                self.sessman.save(session)
            handler.session = session
            session.sessman = self.sessman

