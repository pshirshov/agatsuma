# -*- coding: utf-8 -*-

import tornado.web
import tornado.ioloop
import time
from agatsuma.core import Core
from agatsuma.settings import Settings
from agatsuma.log import log

from agatsuma.interfaces import AbstractSpell, FilteringSpell, SessionHandler
from agatsuma.framework.tornado import AgatsumaHandler, MsgPumpHandler, FidelityWorker
from agatsuma.framework.tornado.interfaces import  HandlingSpell, RequestSpell

class NullSpell(AbstractSpell, FilteringSpell):
    def __init__(self):
        config = {'info' : 'Null spell',
                  'deps' : ()
                 }
        AbstractSpell.__init__(self, 'null_spell', config)

    def filtersList(self):
        return (self.testFilter,)

    def testFilter(self, inp):
        return inp.replace("Hello", "Oh hi")

    def entryPoint(self, *args, **kwargs):
        log.core.info("Demo entry point called with argv %s" % str(args))

    def preConfigure(self, core):
        core.registerOption("!test.rotest", unicode, "Test read-only setting")
        core.registerOption("test.test", unicode, "Test setting")
        core.registerEntryPoint("demoPoint", self.entryPoint)

class DemoSpell(AbstractSpell, HandlingSpell, RequestSpell):
    def __init__(self):
        config = {'name' : 'Demo spell for multiprocessing handlers',
                  'info' : ()
                 }
        AbstractSpell.__init__(self, 'mp_demo_spell', config)

    def preConfigure(self, core):
        import logging
        log.newLogger("test")

    def beforeRequestCallback(self, handler):
        log.test.debug("beforeRequestCallback: %s" % str(handler))
        log.test.debug("request: %s" % str(handler.request))

    def initRoutes(self, map):
        map.extend([(r"/test/mp/worker", MPWorkerHandler),
                    (r"/test/mp/pump", MPPumpHandler),
                    (r"/test/mp/timer", MPWorkerTimerHandler),
                ])

class MPWorkerHandler(AgatsumaHandler, SessionHandler):
    """
    Handler with worker that perform operations in separate
    process. Useful for long-running operations that
    return some result as one value.
    """
    @tornado.web.asynchronous
    def get(self):
      print "GET>", self.session.get("sesskey", None)
      self.session["sesskey"] = "sessval"
      print "GET2>", self.session.get("sesskey", None)
      self.session.save()
      #self.sessman.delete(self.session)
      self.write("Hello from MPWorkerHandler!<br>")
      self.async(self.test, (1, ), self.onWorkerCompleted)
      import random
      Settings.test.test = unicode(random.randint(1000, 9999))
      Settings.save()

    @FidelityWorker
    def test(handlerId, *args):
        for x in range(1, 3):
            log.core.info("test %d" % x)
            time.sleep(1)
        return "some useful result"

    def onWorkerCompleted(self, ret):
        self.write(ret)
        self.finish()

class MPPumpHandler(MsgPumpHandler):
    """
    Handler with worker that perform operations in separate
    process which sends output via Agatsuma's message pump
    into main thread.
    Useful for long-running operations which may return
    result as series of values.
    """
    @tornado.web.asynchronous
    def get(self):
      self.write("Hello, from MPPumpHandler!<br>")
      self.write(Settings.test.test)
      #Settings.test.test = u"Changing option, it will be propagated into all workers"
      self.write("<br/>")
      self.async(self.test, (1, ), self.onWorkerCompleted)

    @FidelityWorker
    def test(handlerId, *args):
        Settings.test.test = u"123123"
        for x in range(1, 15):
            log.core.info("test %d" % x)
            time.sleep(1)
            MsgPumpHandler.sendMessage(handlerId, "Iteration %d completed<br>" % x)
        return 1

    def onWorkerCompleted(self, ret):
        self.storedValue = ret
        self.waitForQueue(self.complete)

    def complete(self):
        ret = self.storedValue
        self.write("Worker returned: %s" % str(ret))
        self.finish()

    def processMessage(self, message):
        self.write(str(message[1]))
        self.flush()

# Warning: useless perversion
import threading
import multiprocessing
class MPWorkerTimerHandler(MsgPumpHandler):
    """
    As MPPumpHandler, this handler demonstrates long-running
    operation in separate thread which uses message pump.

    But in this example worker process doesn't blocks,
    because timer is used.

    This may be useful for long-running operations which requires
    persistent connection, such as web-based chats with polling...
    """
    @tornado.web.asynchronous
    def get(self):
      """
      async writer with sync worker in separate process, with threading.timer
      """
      self.write("Hello from MPWorkerTimerHandler!<br>")
      self.flush()
      self.async(self.test, (1, ), self.onWorkerCompleted)
      self.reallyCompleted = False
      self.ret = None

    @FidelityWorker
    def test(handlerId, *args):
        print "Long-running worker started", args
        t = threading.Timer(4, MPWorkerTimerHandler.onTimer, (handlerId, ))
        t.start()
        return "computed result"

    @staticmethod
    def onTimer(handlerId):
        print "onTimer", multiprocessing.current_process()
        MsgPumpHandler.sendMessage(handlerId, "ololo<br/>")

    def processMessage(self, message):
        self.write(str(message[1]))
        self.reallyCompleted = True
        self.flush()

    def onWorkerCompleted(self, ret = None):
        if self.reallyCompleted:
            if not self.ret:
                self.ret = ret
            print "completed>", self.ret
            self.write(self.ret)
            self.finish()
        else:
            if not self.ret:
                self.ret = ret
            tornado.ioloop.IOLoop.instance().add_timeout(
              time.time() + 1,
              self.async_callback(self.onWorkerCompleted))
