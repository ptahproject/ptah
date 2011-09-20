""" Aplication Root """
import sqlalchemy as sqla
from zope import interface
from zope.component import getSiteManager

import ptah
from memphis import config, view

from tinfo import Type
from node import Session
from container import Container
from events import ContentCreatedEvent
from interfaces import IApplicationRoot


class ApplicationPolicy(object):
    interface.implements(view.INavigationRoot)

    __name__ = ''
    __parent__ = None

    # default acl
    __acl__ = ptah.security.ACL

    def __init__(self, request):
        self.request = request


factories = {}

class ApplicationFactory(object):

    def __init__(self, path, name, title, policy=ApplicationPolicy):
        self.id = '-'.join(part for part in path.split('/') if part)
        self.path = path if path.endswith('/') else '%s/'%path
        self.name = name
        self.title = title
        self.policy = policy

        factories[self.id] = self

        info = config.DirectiveInfo()
        info.attach(
            config.Action(None, discriminator=('ptah-cms:application', path))
            )

    def __call__(self, request=None):
        root = ApplicationRoot.getRoot(name=self.name, title=self.title)

        root.__root_path__ = self.path
        root.__parent__ = self.policy(request)
        if request is not None:
            request.root = root
        return root


class ApplicationRoot(Container):
    interface.implements(IApplicationRoot)

    __root_path__ = '/'

    __type__ = Type('app', 'Application')

    _sql_get_root = ptah.QueryFreezer(
        lambda: Session.query(Container)\
            .filter(sqla.sql.and_(
                    Container.__name_id__ == sqla.sql.bindparam('name'),
                    Container.__type_id__ == 'app')))

    @classmethod
    def getRoot(cls, name='', title='', *args, **kw):
        root = cls._sql_get_root.first(name=name)
        if root is None:
            root = ApplicationRoot(title=title)
            root.__name__ = name
            root.__path__ = '/%s/'%root.__uuid__
            getSiteManager().notify(ContentCreatedEvent(root))

            Session.add(root)
            Session.flush()

        return root

    def __resource_url__(self, request, info):
        return self.__root_path__
