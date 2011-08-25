""" introspect module """
import ptah
from memphis import config
from zope import interface
from interfaces import ISQLAModule


class SQLAModule(ptah.PtahModule):
    config.utility(name='sqla')
    interface.implementsOnly(ISQLAModule)

    name = 'sqla'
    title = 'SQLAlchemy'
    description = 'SQLAlchemy introspection module.'
