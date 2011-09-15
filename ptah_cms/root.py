""" Aplication Root """
import ptah
import sqlalchemy as sqla
from zope import interface
from memphis import config
from pyramid.decorator import reify
from pyramid.traversal import DefaultRootFactory

from tinfo import Type
from node import Base, Session
from container import Container
from interfaces import IApplicationRoot


class ApplicationFactory(object):

    def __init__(self, path, name, title):
        self.path = path
        self.name = name
        self.title = title

        info = config.DirectiveInfo()
        info.attach(
            config.Action(None, discriminator=('ptah-cms:application', path))
            )

    def __call__(self, request=None):
        root = ApplicationRoot.getRoot(
            __path__=self.path,
            name=self.name, title=self.title)

        root.__path__ = self.path
        if request is not None:
            root.__parent__ = DefaultRootFactory(request)
        return root


class ApplicationRoot(Container):
    interface.implements(IApplicationRoot)

    __acl__ = ptah.security.ACL
    __type__ = Type('application', 'Application')

    _sql_get_root = ptah.QueryFreezer(
        lambda: Session.query(Container)\
            .filter(sqla.sql.and_(
                    Container.name == sqla.sql.bindparam('name'),
                    Container.__type_id__=='application')))

    _path = ''

    @classmethod
    def getRoot(cls, name='', title='', *args, **kw):
        root = cls._sql_get_root.first(name=name)
        if root is None:
            root = ApplicationRoot(title=title, name=name)
            Session.add(root)
            Session.flush()

        return root

    @reify
    def __name__(self):
        return ''

    def __resource_url__(self, request, info):
        return self.__path__


@config.handler(config.SettingsInitialized)
def initialize(ev):
    Base.metadata.create_all()
