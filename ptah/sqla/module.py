""" introspect module """
import ptah
import pyramid_sqla as psa
from memphis import config
from zope import interface
from interfaces import ISQLAModule, ITable

metadata = psa.get_base().metadata


class SQLAModule(ptah.PtahModule):
    """ SQLAlchemy instrospection ptah module. """
    config.utility(name='sqla')
    interface.implementsOnly(ISQLAModule)

    name = 'sqla'
    title = 'SQLAlchemy'
    description = 'SQLAlchemy introspection module.'

    def __getitem__(self, key):
        return Table(metadata.tables[key], self, self.request)


class Table(object):
    interface.implements(ITable)

    def __init__(self, table, mod, request):
        self.__name__ = table.name
        self.__parent__ = mod

        self.table = table
        self.request = request
