""" Aplication Root """
import sqlalchemy as sqla
from zope.interface import implementer

import ptah
from ptah.cms.node import Node, set_policy
from ptah.cms.container import Container
from ptah.cms.interfaces import IApplicationRoot, IApplicationPolicy


APPFACTORY_ID = 'ptah.cms:appfactory'

def get_app_factories():
    """ Get all registered application factories """
    return ptah.config.get_cfg_storage(APPFACTORY_ID)


@implementer(IApplicationRoot)
class BaseApplicationRoot(object):
    """ Base application root """

    __root_path__ = '/'

    def __resource_url__(self, request, info):
        return self.__root_path__


class ApplicationRoot(BaseApplicationRoot, Container):
    """ Persistent application root """


@implementer(IApplicationPolicy)
class ApplicationPolicy(object):
    """ Application policy """

    __name__ = ''
    __parent__ = None

    # default acl
    __acl__ = ptah.DEFAULT_ACL

    def __init__(self, request):
        self.request = request


class ApplicationFactory(object):
    """ Application factory """

    type = None

    def __init__(self, cls, path='', name='', title='',
                 policy = ApplicationPolicy, default_root = None,
                 parent_factory = None, config=None):
        self.id = '-'.join(part for part in path.split('/') if part)
        self.path = path if path.endswith('/') else '%s/'%path
        self.name = name
        self.title = title

        self.default_root = default_root
        if (self.path == '/') and default_root is None:
            self.default_root = True

        self.cls = cls
        self.type = cls.__type__
        self.policy = policy
        self.parent_factory = parent_factory

        discr = (APPFACTORY_ID, path)
        intr = ptah.config.Introspectable(
            APPFACTORY_ID, discr, name, APPFACTORY_ID)
        intr['id'] = self.id
        intr['factory'] = self

        if config is not None:
            ptah.config.get_cfg_storage(
                APPFACTORY_ID, registry=config.registry)[self.id] = self

        info = ptah.config.DirectiveInfo()
        info.attach(
            ptah.config.Action(
                lambda cfg: cfg.get_cfg_storage(APPFACTORY_ID)\
                    .update({self.id: self}),
                discriminator=discr, introspectables=(intr,))
            )

        self._sql_get_root = ptah.QueryFreezer(
            lambda: ptah.get_session().query(cls)\
                .filter(sqla.sql.and_(
                    cls.__name_id__ == sqla.sql.bindparam('name'),
                    cls.__type_id__ == sqla.sql.bindparam('type'))))

    def __call__(self, request=None):
        root = self._sql_get_root.first(name=self.name, type=self.type.__uri__)
        if root is None:
            root = self.type.create(title=self.title)
            root.__name_id__ = self.name
            root.__path__ = '/%s/'%root.__uri__
            Session = ptah.get_session()
            Session.add(root)
            Session.flush()

        root.__root_path__ = self.path
        root.__parent__ = policy = self.policy(request)
        root.__default_root__ = self.default_root

        if request is not None:
            set_policy(policy)
            request.root = root

        if self.parent_factory:
            policy.__parent__ = self.parent_factory()

        return root
