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
        
    def initMetadata(self, metadata):
        pass
    
    def updateTableProperties(self, spell, properties, table, Class):
        return properties

    def performDeployment(self):
        pass   
    
    def setupORM(self, core):
        pass
    
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

    def beforeRequestCallback(self, baseController):
        pass

    def globalFiltersList(self):
        return []

    def filtersList(self):
        return []
   """