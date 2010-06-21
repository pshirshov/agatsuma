# -*- coding: utf-8 -*-

import hashlib

import sqlalchemy as sa
import sqlalchemy.orm as orm

import tornado.web
import tornado.ioloop

from agatsuma.core import Core
from agatsuma.settings import Settings
from agatsuma.log import log

from agatsuma.interfaces import AbstractSpell, ModelSpell
from agatsuma.framework.tornado import AgatsumaHandler, FidelityWorker
from agatsuma.framework.tornado.interfaces import  HandlingSpell

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
        """
        self.registerTable({'tableName' : 'users', 'propertyName' : None},
                            sa.Column('id', sa.types.Integer, primary_key=True),
                            sa.Column('name', sa.types.String),
                            sa.Column('password', sa.types.String)
                          )
        self.registerTable({'tableName' : 'posts', 'propertyName' : 'postsTable'})
        """
    def setupORM(self, core):
        userProps = {'posts' : orm.relation(Post, 
                     cascade = "all, delete, delete-orphan",
                     order_by = [self.postsTable.c.id]),
                    }
        postProps = {'user' : orm.relation(User)}
        self.registerMapping(core, User, self.users, properties = userProps)
        self.registerMapping(core, Post, self.postsTable, properties = postProps)   
        
    def postORMSetup(self, core):
        sqlaSpell = Core.instance.spellsDict["agatsuma_sqla"]
        ModelDemoSpell.SqlaSess = sqlaSpell.sqlaDefaultSess

    def initRoutes(self, map):
        map.extend([(r"/test/model/test", ModelTestHandler),
                    (r"/test/model/mptest", ModelMPTestHandler),

                   ])                   
       
    def performDeployment(self, core):
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
