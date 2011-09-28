import ptah
from zope import interface


class ITable(interface.Interface):
    """ table wrapper """


class IRecord(interface.Interface):
    """ record wrapper """


class IField(interface.Interface):
    """ adapter from sqlalchemy column to colander node """
