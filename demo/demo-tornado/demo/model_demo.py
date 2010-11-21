# -*- coding: utf-8 -*-

import hashlib

import sqlalchemy as sa
import sqlalchemy.orm as orm

import tornado.web
import tornado.ioloop

from agatsuma import log
from agatsuma import Spell

from agatsuma.interfaces import AbstractSpell, ModelSpell

from agatsuma.elements import Atom

from agatsuma.web.tornado import AgatsumaHandler, FidelityWorker
from agatsuma.web.tornado.interfaces import  HandlingSpell

class Post(object):
    def __init__(self, message):
        self.message = message

    def __repr__(self):
        return 'msg: "%s"' % self.message

class User(object):
    def __init__(self, name, password):
        self.name = name
        self.password =  hashlib.md5(password).hexdigest()

    def createPost(self, message):
        newPost = Post(message)
        self.posts.append(newPost)

class ModelDemoSpell(AbstractSpell, ModelSpell, HandlingSpell):
    def __init__(self):
        config = {'info' : 'Model demo spell',
                  'deps' : (Atom.agatsuma_sqla,)
                 }
        AbstractSpell.__init__(self, Atom.sqla_demo_spell, config)
        ModelSpell.__init__(self)

    def init_metadata(self, metadata):
        users_table = sa.Table('users',
        metadata,
        sa.Column('id', sa.types.Integer, primary_key=True),
        sa.Column('name', sa.types.String),
        sa.Column('password', sa.types.String)
        )
        self.register_table(users_table)
        posts_table = sa.Table('posts',
        metadata,
        sa.Column('id', sa.types.Integer, primary_key=True),
        sa.Column("user_id" , sa.types.Integer, sa.ForeignKey('users.id')),
        sa.Column('message', sa.types.String),
        )
        self.register_table(posts_table, "postsTable")
        """
        self.register_table({'tableName' : 'users', 'propertyName' : None},
                            sa.Column('id', sa.types.Integer, primary_key=True),
                            sa.Column('name', sa.types.String),
                            sa.Column('password', sa.types.String)
                          )
        self.register_table({'tableName' : 'posts', 'propertyName' : 'postsTable'})
        """
    def setup_orm(self, core):
        userProps = {'posts' : orm.relation(Post,
                     cascade = "all, delete, delete-orphan",
                     order_by = [self.postsTable.c.id]),
                    }
        postProps = {'user' : orm.relation(User)}
        self.register_mapping(core, User, self.users, properties = userProps)
        self.register_mapping(core, Post, self.postsTable, properties = postProps)

    def post_orm_setup(self, core):
        sqlaSpell = Spell(Atom.agatsuma_sqla)
        ModelDemoSpell.SqlaSess = sqlaSpell.sqla_default_session

    def init_routes(self, map):
        map.extend([(r"/test/model/test", ModelTestHandler),
                    (r"/test/model/mptest", ModelMPTestHandler),

                   ])

    def perform_deployment(self, core):
        log.core.debug("Hello from the demo deployment callback. Now we can add objects into DB")
        session = ModelDemoSpell.SqlaSess
        userscount = session.query(User).count()
        newuser = User('user_%d' % (userscount + 1), 'qwerty')
        session.add(newuser)
        session.commit()


class ModelTestHandler(tornado.web.RequestHandler):
    def get(self):
        session = ModelDemoSpell.SqlaSess
        userscount = session.query(User).count()
        self.write("Hello from ModelTestHandler.<br/>Current users count is %d<br/>" % userscount)
        newuser = User('user_%d' % (userscount + 1), 'qwerty')
        session.add(newuser)
        newuser.posts.append(Post("Oh nyaa~!"))
        session.commit()
        self.write("One user added")

class ModelMPTestHandler(AgatsumaHandler):
    @tornado.web.asynchronous
    def get(self):
      self.write("Hello from MPWorkerHandler!<br>")
      self.async(self.test, (1, ), self.onWorkerCompleted)

    @FidelityWorker
    def test(handlerId, *args):
        session=ModelDemoSpell.SqlaSess
        userscount = session.query(User).count()
        ret = "Hello from ModelMPTestHandler.<br/>Current users count is %d<br/>" % userscount
        newuser = User('user_%d' % (userscount + 1), 'qwerty')
        session.add(newuser)
        newuser.posts.append(Post("Oh nyaa~!"))
        session.commit()
        ret += "One user added"
        return ret

    def onWorkerCompleted(self, ret):
        self.write(ret)
        self.finish()

import multiprocessing

class ModelMPStressTestHandler(AgatsumaHandler):
    @tornado.web.asynchronous
    def get(self):
      self.write("Hello from MPWorkerHandler!<br>")
      self.async(self.test, (1, ), self.onWorkerCompleted)

    @FidelityWorker
    def test(handlerId, *args):
        session=ModelDemoSpell.SqlaSess
        ret = "Hello from ModelMPStressTestHandler!"
        for x in range(1,50000):
            userscount = session.query(User).count()
            newuser = User('user_%d' % (userscount + 1), 'qwerty')
            session.add(newuser)
            newuser.posts.append(Post("Oh nyaa~!"))
            if not x % 50:
                session.commit()
            if not x % 100:
                log.core.info("%s: %d" % (str(multiprocessing.current_process().name), x))
            #ret += "One user added"
        return ret

    def onWorkerCompleted(self, ret):
        self.write(ret)
        self.finish()
