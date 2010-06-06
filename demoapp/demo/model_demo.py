# -*- coding: utf-8 -*-

import hashlib

import sqlalchemy as sa
import sqlalchemy.orm as orm

import tornado.web
import tornado.ioloop

from agatsuma.core import Core
from agatsuma.settings import Settings
from agatsuma.log import log

from agatsuma.interfaces import AbstractSpell, HandlingSpell, ModelSpell
from agatsuma.handlers import AgatsumaHandler, MsgPumpHandler, FidelityWorker

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
                  'deps' : ("agatsuma_sqla",)
                 }
        AbstractSpell.__init__(self, 'sqla_demo_spell', config)
        ModelSpell.__init__(self)

    def initMetadata(self, metadata):
        users_table = sa.Table('users',
                            metadata,
                            sa.Column('id', sa.types.Integer, primary_key=True),
                            sa.Column('name', sa.types.String),
                            sa.Column('password', sa.types.String)
        )
        self.registerTable(users_table)
        posts_table = sa.Table('posts',
                            metadata,
                            sa.Column('id', sa.types.Integer, primary_key=True),
                            sa.Column("user_id" , sa.types.Integer, sa.ForeignKey('users.id')),
                            sa.Column('message', sa.types.String),
        )        
        self.registerTable(posts_table, "postsTable")
        
    def performDeployment(self):
        spell = Core.instance.spellsDict["agatsuma_sqla"]  
        spell.meta.drop_all()
        spell.meta.create_all()
        
    def setupORM(self, core):
        userProps = {'posts' : orm.relation(Post, 
                     cascade = "all, delete, delete-orphan",
                     order_by = [self.postsTable.c.id]),
                    }
        postProps = {'user' : orm.relation(User)}
        self.registerMapping(core, User, self.users, properties = userProps)
        self.registerMapping(core, Post, self.postsTable, properties = postProps)   
        
    def initRoutes(self, map):
        map.extend([(r"/test/model/recreate", DBRecreateHandler),
                    (r"/test/model/test", ModelTestHandler),
                    (r"/test/model/mptest", ModelMPTestHandler),
                   ])
                   
class DBRecreateHandler(tornado.web.RequestHandler):
    def get(self):
        spell = self.application.spellsDict["sqla_demo_spell"]  
        spell.performDeployment()
        
class ModelTestHandler(tornado.web.RequestHandler):
    def get(self):
        session=self.application.SqlaSess # self.application == Core.instance
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
        session=Core.SqlaSess
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
