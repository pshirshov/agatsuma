# -*- coding: utf-8 -*-

class IModelSpell(object):
    def __init__(self):
        self.__tables = {}

    def register_table(self, table, attrName = None):
        if not attrName:
            attrName = table.name
        if not ((getattr(self, attrName, None) is not None) or (table in self.__tables.values())):
            setattr(self, attrName, table)
        else:
            raise Exception("Table '%s' already registered" % attrName)
        self.__tables[attrName] = table

    def register_mapping(self, core, ClassToMap, tableToMap, **kwargs):
        import sqlalchemy.orm as orm
        properties = kwargs.get("properties", {})
        spells = core.spellbook.implementations_of(IModelSpell)
        for spell in spells:
            properties = spell.update_table_properties(self, properties, tableToMap, ClassToMap)
        orm.mapper(ClassToMap, tableToMap, properties)

    def update_table_structure(self, spell, tableName, *args, **kwargs):
        return (args, kwargs)

    def update_table_properties(self, spell, properties, table, Class):
        return properties

    def init_metadata(self, metadata):
        pass

    def setup_orm(self, core):
        pass

    def post_orm_setup(self, core):
        """:ref:`SQLAlchemy driver<sqla-driver>` calls this callback after setup_orm calls

:param core: Core instance
        """
        pass

    def perform_deployment(self, core):
        pass
