# -*- coding: utf-8 -*-

import copy

from agatsuma.core import Core

if Core.internal_state.get("mode", None) == "normal":
    import sqlalchemy as sa
    import sqlalchemy.orm as orm
else:
    sa = None

from agatsuma import log
from agatsuma import Settings
from agatsuma import Implementations

from agatsuma.interfaces import AbstractSpell, IInternalSpell
from agatsuma.interfaces import IStorageSpell, IModelSpell, ISetupSpell

from agatsuma.commons.types import Atom

class SQLASpell(AbstractSpell, IInternalSpell, IStorageSpell, ISetupSpell):
    """.. _sqla-driver:

    """
    def __init__(self):
        config = {'info' : 'Agatsuma SQLAlchemy Spell',
                  'deps' : (Atom.agatsuma_core, ),
                  'provides' : (Atom.storage_driver, ),
                 }
        AbstractSpell.__init__(self, Atom.agatsuma_sqla, config)
        if sa:
            SQLASpell.proto_metadata = sa.MetaData()

    def requirements(self):
        return {"sqla" : ["sqlalchemy>=0.6.1"],
               }

    def deploy(self, *args, **kwargs):
        spells = Implementations(IModelSpell)
        log.storage.info("Initializing Database...")
        if spells:
            if "recreate" in args:
                log.storage.info("Recreating schema...")
                self.meta.drop_all()
                self.meta.create_all()
            for spell in spells:
                spell.perform_deployment(Core.instance)
            log.storage.info("Deployment completed")
        else:
            log.storage.info("Model spells not found")

    def pre_configure(self, core):
        core.register_option("!sqla.uri", unicode, "SQLAlchemy engine URI")
        core.register_option("!sqla.parameters", dict, "kwargs for create_engine")
        core.register_entry_point("agatsuma:sqla_init", self.deploy)

    def post_configure(self, core):
        spells = Implementations(IModelSpell)
        if spells:
            log.storage.info("Initializing SQLAlchemy engine and session...")
            self.SqlaEngine = sa.create_engine(Settings.sqla.uri, **Settings.sqla.parameters)
            SessionFactory = orm.sessionmaker()
            self.Session = orm.scoped_session(SessionFactory)
            self.Session.configure(bind=self.SqlaEngine)

            log.storage.info("Initializing SQLAlchemy data model..")
            for spell in spells:
                spell.init_metadata(SQLASpell.proto_metadata)
            SQLASpell.meta = SQLASpell.metadata_copy()
            SQLASpell.meta.bind = self.SqlaEngine
            log.storage.info("Setting up ORM...")
            for spell in spells:
                spell.setup_orm(core)
            log.storage.info("Model initialized")

            self.sqla_default_session = self.makeSession()
            for spell in spells:
                spell.post_orm_setup(core)
        else:
            log.storage.info("Model spells not found")

    def makeSession(self):
        """
        Instantiates new session using ScopedSession helper
        """
        return self.Session()

    @staticmethod
    def metadata_copy():
        meta = copy.deepcopy(SQLASpell.proto_metadata)
        # little bugfix
        meta.ddl_listeners = sa.util.defaultdict(list)
        return meta
