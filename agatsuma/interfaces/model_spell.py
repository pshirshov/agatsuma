# -*- coding: utf-8 -*-

import sqlalchemy.orm as orm

class ModelSpell(object):
    def __init__(self):
        self.__tables = {}       

    def registerTable(self, table, attrName = None):
        if not attrName:
            attrName = table.name           
        if not ((getattr(self, attrName, None) is not None) or (table in self.__tables.values())):
            setattr(self, attrName, table)
        else:
            raise Exception("Table '%s' already registered" % attrName)
        self.__tables[attrName] = table
    
    def registerMapping(self, core, ClassToMap, tableToMap, **kwargs):
        properties = kwargs.get("properties", {})
        spells = core._implementationsOf(ModelSpell)
        for spell in spells:
            properties = spell.updateTableProperties(self, properties, tableToMap, ClassToMap)
        orm.mapper(ClassToMap, tableToMap, properties)
    
    def updateTableStructure(self, spell, tableName, *args, **kwargs):
        return (args, kwargs)

    def updateTableProperties(self, spell, properties, table, Class):
        return properties
        
    def initMetadata(self, metadata):
        pass

    def setupORM(self, core):
        pass
 
    def postORMSetup(self, core):
        """:ref:`SQLAlchemy driver<sqla-driver>` calls this callback after setupORM calls

:param core: Core instance
        """
        pass

    def performDeployment(self, core):
        pass   
    
