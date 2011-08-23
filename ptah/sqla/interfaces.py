import ptah
from zope import interface


class ISQLAModule(ptah.IPtahModule):
    """ sqla introspection module """


class ITable(interface.Interface):
    """ """
