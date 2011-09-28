""" introspect module """
import ptah
import pyramid_sqla as psa
from memphis import config
from zope import interface
from interfaces import ITable, IRecord

Session = psa.get_session()
metadata = psa.get_base().metadata


class SQLAModule(ptah.PtahModule):
    """ SQLAlchemy instrospection module. """

    title = 'SQLAlchemy'
    ptah.manageModule('sqla')

    metadata = {}

    def __getitem__(self, key):
        try:
            id, table = key.split('-', 1)
        except:
            raise KeyError(key)

        md = self.metadata[id][0]
        return Table(md.tables[table], self, self.request)

    @classmethod
    def addMetadata(cls, md, id, title=''):
        cls.metadata[id] = [md, title or id.capitalize()]

addMetadata = SQLAModule.addMetadata
addMetadata(metadata, 'psqla', 'Pyramid sqla')


class Table(object):
    interface.implements(ITable)

    def __init__(self, table, mod, request):
        self.__name__ = table.name
        self.__parent__ = mod

        self.table = table
        self.request = request

    def __getitem__(self, key):
        if key == 'add.html':
            raise KeyError(key)

        try:
            return Record(key, self.table, self, self.request)
        except:
            raise KeyError(key)


class Record(object):
    interface.implements(IRecord)

    def __init__(self, pid, table, parent, request):
        self.pid = pid
        self.table = table
        self.request = request

        self.__name__ = str(pid)
        self.__parent__ = parent

        self.pname = None
        self.pcolumn = None
        for cl in table.columns:
            if cl.primary_key:
                self.pname = cl.name
                self.pcolumn = cl

        self.data = Session.query(table).filter(
            self.pcolumn == pid).one()
