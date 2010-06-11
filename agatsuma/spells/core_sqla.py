# -*- coding: utf-8 -*-

import copy

import sqlalchemy as sa
import sqlalchemy.orm as orm

from agatsuma.log import log
from agatsuma.settings import Settings
from agatsuma.core import Core

from agatsuma.interfaces import AbstractSpell, ModelSpell
        
class SQLASpell(AbstractSpell):
    def __init__(self):
        config = {'info' : 'Agatsuma SQLAlchemy Spell',
                  'deps' : ('agatsuma_core', )
                 }
        AbstractSpell.__init__(self, 'agatsuma_sqla', config)
        SQLASpell.protoMeta = sa.MetaData() 

    def deploy(self, argv):
        spells = Core.instance._implementationsOf(ModelSpell)
        log.core.info("Initializing Database...")
        if spells:
            if "recreate" in argv:
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
            SessionClass = orm.sessionmaker()
            Session = orm.scoped_session(SessionClass)
            Session.configure(bind=self.SqlaEngine)
            self.SqlaSess = Session()
            log.core.info("Initializing SQLAlchemy data model..")
            for spell in spells:
                spell.initMetadata(SQLASpell.protoMeta)
            SQLASpell.meta = SQLASpell.metaCopy()
            SQLASpell.meta.bind = self.SqlaEngine
            log.core.info("Setting up ORM...")
            for spell in spells:
                spell.setupORM(core)
            log.core.info("Model initialized")
        else:
            log.core.info("Model spells not found")
            
    @staticmethod
    def metaCopy():
        meta = copy.deepcopy(SQLASpell.protoMeta)
        # little bugfix
        meta.ddl_listeners = sa.util.defaultdict(list)
        return meta
       
