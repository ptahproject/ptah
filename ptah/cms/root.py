""" Aplication Root """
import sqlalchemy as sqla
import ptah
from ptah import config
from zope import interface

from node import Node, Session, set_policy
from container import Container
from interfaces import IApplicationRoot, IApplicationPolicy


APPFACTORY_ID = 'ptah.cms:appfactory'

def get_app_factories():
    return config.get_cfg_storage(APPFACTORY_ID)


class ApplicationRoot(Container):
    interface.implements(IApplicationRoot)

    __root_path__ = '/'

    def __resource_url__(self, request, info):
        return self.__root_path__


class ApplicationPolicy(object):
    interface.implements(IApplicationPolicy)

    __name__ = ''
    __parent__ = None

    # default acl
    __acl__ = ptah.DEFAULT_ACL

    def __init__(self, request):
        self.request = request


class ApplicationFactory(object):

    def __init__(self, factory, path='', name='', title='',
                 policy = ApplicationPolicy, default_root = None, config=None):
        self.id = '-'.join(part for part in path.split('/') if part)
        self.path = path if path.endswith('/') else '%s/'%path
        self.name = name
        self.title = title

        self.default_root = default_root
        if not path and default_root is None:
            self.default_root = True

        if isinstance(factory, type) and issubclass(factory, Node):
            factory = factory.__type__

        self.factory = factory
        self.policy = policy

        if config is not None:
            ptah.config.get_cfg_storage(
                APPFACTORY_ID, registry=config.registry)[self.id] = self

        info = ptah.config.DirectiveInfo()
        info.attach(
            ptah.config.Action(
                lambda cfg: cfg.get_cfg_storage(APPFACTORY_ID)\
                    .update({self.id:self}),
                discriminator=(APPFACTORY_ID, path))
            )

    _sql_get_root = ptah.QueryFreezer(
        lambda: Session.query(Container)\
            .filter(sqla.sql.and_(
                    Container.__name_id__ == sqla.sql.bindparam('name'),
                    Container.__type_id__ == sqla.sql.bindparam('type'))))

    def __call__(self, request=None):
        root = self._sql_get_root.first(
            name=self.name, type=self.factory.__uri__)
        if root is None:
            root = self.factory.create(title=self.title)
            root.__name_id__ = self.name
            root.__path__ = '/%s/'%root.__uri__
            Session.add(root)
            Session.flush()

        root.__root_path__ = self.path
        root.__parent__ = policy = self.policy(request)
        root.__default_root__ = self.default_root

        set_policy(policy)

        if request is not None:
            request.root = root
        return root
