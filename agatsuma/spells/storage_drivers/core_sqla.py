# -*- coding: utf-8 -*-

import copy

from agatsuma.core import Core

if Core.internalState.get("mode", None) == "normal":
    import sqlalchemy as sa
    import sqlalchemy.orm as orm
else:
    sa = None

from agatsuma.log import log
from agatsuma.settings import Settings
from agatsuma.core import Core

from agatsuma.interfaces import AbstractSpell, StorageSpell, ModelSpell

class SQLASpell(AbstractSpell, StorageSpell):
    """.. _sqla-driver:
    
    """
    def __init__(self):
        config = {'info' : 'Agatsuma SQLAlchemy Spell',
                  'deps' : ('agatsuma_core', ),
                  'provides' : ('storage_driver', ),
                 }
        AbstractSpell.__init__(self, 'agatsuma_sqla', config)
        if sa:
            SQLASpell.protoMeta = sa.MetaData()
            
    def requirements(self):
        return {"sqla" : ["sqlalchemy>=0.6.1"],
               }

    def deploy(self, *args, **kwargs):
        spells = Core.instance._implementationsOf(ModelSpell)
        log.core.info("Initializing Database...")
        if spells:
            if "recreate" in args:
                log.core.info("Recreating schema...")
                self.meta.drop_all()
                self.meta.create_all()
            for spell in spells:
                spell.performDeployment(Core.instance)
            log.core.info("Deployment completed")
        else:
            log.core.info("Model spells not found")

    def preConfigure(self, core):
        core.registerOption("!sqla.uri", unicode, "SQLAlchemy engine URI")
        core.registerOption("!sqla.parameters", dict, "kwargs for create_engine")
        core.registerEntryPoint("agatsuma:sqla_init", self.deploy)

    def postConfigure(self, core):
        spells = core._implementationsOf(ModelSpell)
        if spells:
            log.core.info("Initializing SQLAlchemy engine and session...")
            self.SqlaEngine = sa.create_engine(Settings.sqla.uri, **Settings.sqla.parameters)
            SessionFactory = orm.sessionmaker()
            self.Session = orm.scoped_session(SessionFactory)
            self.Session.configure(bind=self.SqlaEngine)
            
            log.core.info("Initializing SQLAlchemy data model..")
            for spell in spells:
                spell.initMetadata(SQLASpell.protoMeta)
            SQLASpell.meta = SQLASpell.metaCopy()
            SQLASpell.meta.bind = self.SqlaEngine
            log.core.info("Setting up ORM...")
            for spell in spells:
                spell.setupORM(core)
            log.core.info("Model initialized")

            self.sqlaDefaultSess = self.makeSession()
            for spell in spells:
                spell.postORMSetup(core)
        else:
            log.core.info("Model spells not found")

    def makeSession(self):
        """
        Instantiates new session using ScopedSession helper
        """
        return self.Session()

    @staticmethod
    def metaCopy():
        meta = copy.deepcopy(SQLASpell.protoMeta)
        # little bugfix
        meta.ddl_listeners = sa.util.defaultdict(list)
        return meta
       
