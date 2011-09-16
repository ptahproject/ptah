""" Aplication Root """
import sqlalchemy as sqla
from zope import interface
from zope.component import getSiteManager

import ptah
from memphis import config

from tinfo import Type
from node import Session
from container import Container
from policy import ApplicationPolicy
from events import ContentCreatedEvent
from interfaces import IApplicationRoot


factories = {}

class ApplicationFactory(object):

    def __init__(self, path, name, title, policy=ApplicationPolicy):
        self.path = path
        self.name = name
        self.title = title
        self.policy = policy

        factories[name] = self

        info = config.DirectiveInfo()
        info.attach(
            config.Action(None, discriminator=('ptah-cms:application', path))
            )

    def __call__(self, request=None):
        root = ApplicationRoot.getRoot(name=self.name, title=self.title)

        root.__root_path__ = self.path
        root.__parent__ = self.policy(request)
        return root


class ApplicationRoot(Container):
    interface.implements(IApplicationRoot)

    __type__ = Type('app', 'Application')

    _sql_get_root = ptah.QueryFreezer(
        lambda: Session.query(Container)\
            .filter(sqla.sql.and_(
                    Container.name == sqla.sql.bindparam('name'),
                    Container.__type_id__=='app')))

    __root_path__ = '/'

    @classmethod
    def getRoot(cls, name='', title='', *args, **kw):
        root = cls._sql_get_root.first(name=name)
        if root is None:
            root = ApplicationRoot(name=name, title=title)
            root.__path__ = '/%s/'%root.__uuid__
            getSiteManager().notify(ContentCreatedEvent(root))

            Session.add(root)
            Session.flush()

        return root

    def __resource_url__(self, request, info):
        return self.__root_path__

    @property
    def __acl__(self):
        acl = self._acl_()
        acl.extend(ptah.security.ACL)
        return acl
