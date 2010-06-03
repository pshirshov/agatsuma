# -*- coding: utf-8 -*-

import sqlalchemy.orm as orm

class ModelSpell(object):
    def initMetadata(self, metadata):
        pass

    def registerTable(self, table):
        if not getattr(self, table.name, None):
            setattr(self, table.name, table)
        else:
            raise Exception("Table '%s' already registered" % table.name)
            #self.tables = {}
        #self.tables[table.name] = table

    def updateTableProperties(self, spell, properties, table, Class):
        return properties

    def performDeployment(self):
        pass   
    
    def setupORM(self, core):
        pass
    
    def registerMapping(self, core, ClassToMap, tableToMap, **kwargs):
        properties = kwargs.get("properties", {})
        spells = core._implementationsOf(ModelSpell)
        for spell in spells:
            properties = spell.updateTableProperties(self, properties, tableToMap, ClassToMap)
        orm.mapper(ClassToMap, tableToMap, properties)
        

    """
    # UNUSED FOR NOW...
    #TODO: temporary ?
    def spellName(self):
        return self.__pName

    # new methods
    def updateGlobals(self, globj):
        pass

    def entryPointsList(self):
        return []

    def initORM(self, orm, engine, dialectProps, propDict):
        pass

    def extendORMProperties(self, orm, engine, dialectProps, propDict):
        pass

    def deployCallback(self):
        pass

    def beforeRequestCallback(self, baseController):
        pass

    def globalFiltersList(self):
        return []

    def filtersList(self):
        return []
   """