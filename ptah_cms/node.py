""" Node implementation """
import ptah
import pyramid_sqla
import sqlalchemy as sqla
from zope import interface
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden

from interfaces import INode

Base = pyramid_sqla.get_base()
Session = pyramid_sqla.get_session()


class Node(Base):
    """ Base class for content objects.

    .. attribute:: __uri__

       Unique object id. *Required*

    .. attribute:: __type__

       Type information object :py:class:`ptah_cms.TypeInformation`

    .. attribute:: __parent__

       Parent of node. Ptah doesn't load `__parent__` automatically.
       To load node parents use :py:func:`ptah_cms.loadParents` function.

    .. attribute:: __owner__

       URI of owner principal. It possible to load principal object
       by using :py:func:`ptah.resolve` function.

    .. attribute:: __local_roles__

    .. attribute:: __acls__

    .. attribute:: __uri_generator__

    """

    interface.implements(INode,
                         ptah.IACLsAware,
                         ptah.IOwnersAware,
                         ptah.ILocalRolesAware)

    __tablename__ = 'ptah_cms_nodes'

    __id__ = sqla.Column('id', sqla.Integer, primary_key=True)
    __type_id__ = sqla.Column('type', sqla.String)
    __type__ = None

    __uri__ = sqla.Column('uri', sqla.String, unique=True, nullable=False)
    __parent_uri__ = sqla.Column('parent', sqla.String,sqla.ForeignKey(__uri__))

    __owner__ = sqla.Column('owner', sqla.String, default='')
    __local_roles__ = sqla.Column('roles', ptah.JsonDictType(), default={})
    __acls__ = sqla.Column('acls', ptah.JsonListType(), default=[])

    __children__ = sqla.orm.relationship(
        'Node',
        backref=sqla.orm.backref('__parent_ref__',remote_side=[__uri__]))

    __mapper_args__ = {'polymorphic_on': __type_id__}

    __parent__ = None
    __uri_generator__ = None

    __acl__ = ptah.ACLsProperty()

    def __init__(self, **kw):
        self.__owners__ = []
        self.__local_roles__ = {}
        self.__permissions__ = []

        for attr, value in kw.items():
            setattr(self, attr, value)

        if '__parent__' in kw and kw['__parent__'] is not None:
            self.__parent_uri__ = kw['__parent__'].__uri__

        try:
            self.__uri__ = self.__uri_generator__()
        except TypeError: # pragma: no cover
            raise TypeError(
                'Subclass of Node has to override __uri_generator__')


def load(uri, permission=None):
    """ Load node by `uri` and initialize __parent__ attributes. Also checks
    permission if permissin is specified.

    :param uri: Node uri
    :param permission: Check permission on node object
    :type permission: Permission id or None
    :raise KeyError: Node with this uri is not found.
    :raise HTTPForbidden: If current principal doesn't pass permission check on loaded node.
    """
    item = ptah.resolve(uri)

    if item is not None:
        loadParents(item)

        if permission is not None:
            if not ptah.checkPermission(permission, item):
                raise HTTPForbidden()
    else:
        raise HTTPNotFound(uri)

    return item


def loadParents(node):
    """ Load and initialize `__parent__` attribute for node. 
    Returns list of loaded parents. 
    """
    parents = []
    parent = node
    while parent is not None:
        if not isinstance(parent, Node): # pragma: no cover
            break

        if parent.__parent__ is None:
            parent.__parent__ = parent.__parent_ref__

        parent = parent.__parent__

        if parent is not None:
            parents.append(parent)

    return parents
