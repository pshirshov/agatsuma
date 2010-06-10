# -*- coding: utf-8 -*-

from agatsuma.log import log

from agatsuma.interfaces import AbstractSpell, HandlingSpell
        
class CoreSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Core Spell',
                  'deps' : ()
                 }
        AbstractSpell.__init__(self, 'agatsuma_core', config)
        
    def preConfigure(self, core):
        core.registerOption("!core.debug", bool, "Debug mode")
        core.registerOption("!core.debug_level", int, "Debug level. Possible values: 0, 1 (debug message pump), 2 (debug threads)")
        core.registerOption("!core.workers", int, "Size of working processes pool")
        core.registerOption("!core.settings_update_timeout", int, "Update timeout for workers (sec)")
        core.registerOption("!core.pidfile", unicode, "File with PIDs of all Agatsuma's processes")

    def postConfigure(self, core):
        log.core.info("Initializing URI map..")
        spells = core._implementationsOf(HandlingSpell)
        if spells:
            for spell in spells:
                spell.initRoutes(core.URIMap)
            for spell in spells:
                spell.postInitRoutes(core.URIMap)
            log.core.info("URI map initialized")    
            #log.core.debug("URI map:\n%s" % '\n'.join(map(lambda x: str(x), self.core.URIMap)))
            log.core.debug("URI map:")  
            for p in core.URIMap:
                log.core.debug("* %s" % str(p))  
        else:
            raise Exception("Handling spells not found!")
        
class TornadoSpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Tornado Spell',
                  'deps' : ()
                 }
        AbstractSpell.__init__(self, 'agatsuma_tornado', config)
        
    def preConfigure(self, core):
        core.registerOption("!tornado.port", int, "Web server port")
        core.registerOption("!tornado.cookie_secret", unicode, "cookie secret")
        core.registerOption("!tornado.parameters", dict, "Kwarg parameters for tornado application")
        core.registerOption("!tornado.message_pump_timeout", int, "Message pushing interval (msec)")
        core.registerOption("!tornado.logger_pump_timeout", int, "Logging output interval (msec)")

from agatsuma.interfaces import RequestSpell
from agatsuma.session.base_session_manager import DummySessionManager
import datetime

class SessionSpell(AbstractSpell, RequestSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma Session Spell',
                  'deps' : ()
                 }
        AbstractSpell.__init__(self, 'agatsuma_session', config)
        
    def preConfigure(self, core):
        core.registerOption("!sessions.storage_uri", unicode, "Storage URI")
        core.registerOption("!sessions.expiration_interval", int, "Default session length in seconds")

    def postConfigure(self, core):
        log.core.info("Initializing Session Storage..")
        self.sessman = DummySessionManager() # TODO: select appropriate session class
        
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
            session = self.sessman.new(handler.request.remote_ip, handler.request.headers["User-Agent"])
            session.handler = handler
            self.sessman.save(session)
        handler.session = session
        session.sessman = self.sessman
        #handler.sessman = self.sessman
                    
       
