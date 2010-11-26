# -*- coding: utf-8 -*-
import datetime
import re

from agatsuma import SpellByStr
from agatsuma import Settings
from agatsuma import log

from agatsuma.interfaces import AbstractSpell, IInternalSpell
from agatsuma.web.tornado.interfaces import IRequestSpell, ISessionHandler

from agatsuma.commons.types import Atom

class SessionSpell(AbstractSpell, IInternalSpell, IRequestSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Session Spell',
                  'deps' : (Atom.agatsuma_tornado, ),
                  'requires' : (Atom.session_backend, ),
                 }
        AbstractSpell.__init__(self, Atom.agatsuma_session, config)

    def pre_configure(self, core):
        log.new_logger("sessions")
        core.register_option("!sessions.storage_uris", list, "Storage URIs")
        core.register_option("!sessions.expiration_interval", int, "Default session length in seconds")

    def post_configure(self, core):
        log.sessions.info("Initializing Session Storage..")
        rex = re.compile(r"^(\w+)\+(.*)$")
        self.sessmans = []
        for uri in Settings.sessions.storage_uris:
            match = rex.match(uri)
            if match:
                managerId = match.group(1)
                uri = match.group(2)
                spellName = "tornado_session_backend_%s" % managerId
                spell = SpellByStr(spellName)
                if spell:
                    self.sessmans.append(spell.instantiate_backend(uri))
                else:
                    raise Exception("Session backend improperly configured, spell '%s' not found" % spellName)
            else:
                raise Exception("Incorrect session storage URI")

    def save_session(self, session):
        for sessman in self.sessmans:
            sessman.save(session)

    def delete_session(self, session):
        for sessman in self.sessmans:
            sessman.delete(session)

    def before_request_callback(self, handler):
        if isinstance(handler, ISessionHandler):
            cookie = handler.get_secure_cookie("AgatsumaSessId")
            log.sessions.debug("Loading session for %s" % cookie)
            session = None
            if cookie:
                for sessman in self.sessmans:
                    session = sessman.load(cookie)
                    if session:
                        session.handler = handler
                        # Update timestamp if left time < than elapsed time
                        timestamp = session["timestamp"]
                        now = datetime.datetime.now()
                        elapsed = now - timestamp
                        left = (sessman._session_doomsday(timestamp)- now)
                        if elapsed >= left:
                            log.sessions.debug("Updating timestamp for session %s (E: %s, L: %s)" %
                                               (cookie, str(elapsed), str(left)))
                            self.save_session(session)
                        break
            if not session:
                session = self.sessmans[0].new(handler.request.remote_ip,
                                           handler.request.headers["User-Agent"])
                session.handler = handler
                self.save_session(session)
            handler.session = session
            session.sessSpell = self
