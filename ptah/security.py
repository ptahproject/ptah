from collections import OrderedDict
from pyramid.compat import string_types
from pyramid.location import lineage
from pyramid.security import ACLDenied, ACLAllowed, Allow, Deny
from pyramid.security import ALL_PERMISSIONS, NO_PERMISSION_REQUIRED
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.threadlocal import get_current_registry
from pyramid.httpexceptions import HTTPForbidden

import ptah
from ptah import config
from ptah import auth_service
from ptah import SUPERUSER_URI
from ptah.settings import get_settings
from ptah.interfaces import IOwnersAware
from ptah.interfaces import ILocalRolesAware


ID_ACL = 'ptah:aclmap'
ID_ROLE = 'ptah:role'
ID_ROLES_PROVIDER = 'ptah:roles-provider'
ID_PERMISSION = 'ptah:permission'


def get_acls():
    """ return list of registered ACLS """
    return config.get_cfg_storage(ID_ACL)


def get_roles():
    """ return list of registered roles """
    return config.get_cfg_storage(ID_ROLE)


def get_permissions():
    """ return list of registered permissions """
    return config.get_cfg_storage(ID_PERMISSION)


class PermissionInfo(str):
    """ Permission information """

    title = ''
    description = ''


def Permission(name, title, description=''):
    """ Register new permission. """
    info = config.DirectiveInfo()

    permission = PermissionInfo(name)
    permission.title = title
    permission.description = description

    discr = (ID_PERMISSION, name)
    intr = config.Introspectable(ID_PERMISSION, discr, title, ID_PERMISSION)
    intr['permission'] = permission
    intr['module'] = info.module.__name__
    intr['codeinfo'] = info.codeinfo

    info.attach(
        config.Action(
            lambda config, p: \
                config.get_cfg_storage(ID_PERMISSION).update({str(p): p}),
            (permission,), discriminator=discr, introspectables=(intr,))
        )

    return permission


class ACL(list):
    """ Named ACL map

    ACL contains list of permit rules, for example::

      >> acl = ACL('test', 'Test ACL')
      >> acl.allow('system.Everyone', 'View')
      >> acl.deny('system.Everyone', 'Edit')

      >> list(acl)
      [(Allow, 'system.Everyone', ('View',)),
       (Deny, 'system.Everyone', ('Edit',))]

    """

    # do we need somthing like Unset, to unset permission from parent

    def __init__(self, id, title, description=''):
        self.id = id
        self.title = title
        self.description = description

        info = config.DirectiveInfo()
        discr = (ID_ACL, id)
        intr = config.Introspectable(ID_ACL, discr, title, ID_ACL)
        intr['acl'] = self
        intr['codeinfo'] = info.codeinfo

        info.attach(
            config.Action(
                lambda config, p: \
                    config.get_cfg_storage(ID_ACL).update({id: p}),
                (self,), discriminator=discr, introspectables=(intr,))
            )
        self.directiveInfo = info

    def get(self, typ, role):
        for r in self:
            if r[0] == typ and r[1] == role:
                return r

        return None

    def allow(self, role, *permissions):
        """ Give permissions to role """

        if not isinstance(role, string_types):
            role = role.id

        rec = self.get(Allow, role)
        if rec is None:
            rec = [Allow, role, set()]
            self.append(rec)

        if rec[2] is ALL_PERMISSIONS:
            return

        if ALL_PERMISSIONS in permissions:
            rec[2] = ALL_PERMISSIONS
        else:
            rec[2].update(permissions)

    def deny(self, role, *permissions):
        """ Deny permissions for role """

        if not isinstance(role, string_types):
            role = role.id

        rec = self.get(Deny, role)
        if rec is None:
            rec = [Deny, role, set()]
            self.append(rec)

        if rec[2] is ALL_PERMISSIONS:
            return

        if ALL_PERMISSIONS in permissions:
            rec[2] = ALL_PERMISSIONS
        else:
            rec[2].update(permissions)

    def unset(self, role, *permissions):
        """ Unset any previously defined permissions """
        for perm in permissions:
            for rec in self:
                if role is not None and rec[1] != role:
                    continue

                if rec[2] is ALL_PERMISSIONS or perm is ALL_PERMISSIONS:
                    rec[2] = set()
                else:
                    if perm in rec[2]:
                        rec[2].remove(perm)

        records = []
        for rec in self:
            if rec[2]:
                records.append(rec)
        self[:] = records


class ACLsMerge(object):
    """ Special class that merges different ACLs maps """

    def __init__(self, acls):
        self.acls = acls

    def __iter__(self):
        acls = config.get_cfg_storage(ID_ACL)
        for aname in self.acls:
            acl = acls.get(aname)
            if acl is not None:
                for rec in acl:
                    yield rec


class ACLsProperty(object):
    """ This property merges `__acls__` list of ACLs and
    generate one `__acl__`

    For example::

      >> class Content(object):
      ...
      ...   __acls__ = ['map1', 'map2']
      ...
      ...   __acl__ = ACLsProperty()

    In this case it is possible to manipulate permissions
    by just changing `__acls__` list.

    """

    def __get__(self, inst, klass):
        acls = getattr(inst, '__acls__', ())
        if acls:
            return ACLsMerge(acls)
        else:
            return ()


class Role(object):
    """ Register new security role in the system """

    def __init__(self, name, title, description='',
                 prefix='role:', system=False):
        id = '%s%s' % (prefix, name)

        self.id = id
        self.name = name
        self.title = title
        self.description = description
        self.system = system

        self.allowed = set()
        self.denied = set()

        # conflict detection and introspection
        info = config.DirectiveInfo()

        discr = (ID_ROLE, name)
        intr = config.Introspectable(ID_ROLE, discr, title, ID_ROLE)
        intr['role'] = self
        intr['codeinfo'] = info.codeinfo

        info.attach(
            config.Action(
                lambda config, r: \
                    config.get_cfg_storage(ID_ROLE).update({r.name: r}),
                (self, ), discriminator=discr, introspectables=(intr,))
            )

    def __str__(self):
        return 'Role<%s>' % self.title

    def __repr__(self):
        return self.id

    def allow(self, *permissions):
        DEFAULT_ACL.allow(self.id, *permissions)

    def deny(self, *permissions):
        DEFAULT_ACL.deny(self.id, *permissions)

    def unset(self, *permissions):
        DEFAULT_ACL.unset(self.id, *permissions)


class roles_provider(object):
    """ Register roles provider.

    roles provider accepts userid and registry and returns
    sequence of roles.

    :param name: Unique name

    Roles provider interface :py:func:`ptah.interfaces.roles_provider`.

    .. code-block:: python

       import ptah

       @ptah.roles_provider('custom-roles')
       def custom_roles(context, userid, registry):
           if userid == '...':
               return ['Role1', 'Role2']
    """

    def __init__(self, name, __depth=1):
        self.info = config.DirectiveInfo(__depth)
        self.discr = (ID_ROLES_PROVIDER, name)

        self.intr = intr = config.Introspectable(
            ID_ROLES_PROVIDER, self.discr, name, ID_ROLES_PROVIDER)

        intr['name'] = name
        intr['codeinfo'] = self.info.codeinfo

    def __call__(self, factory, cfg=None):
        intr = self.intr
        intr['factory'] = factory

        self.info.attach(
            config.Action(
                lambda cfg, name, f:
                    cfg.get_cfg_storage(ID_ROLES_PROVIDER).update({name: f}),
                (intr['name'], factory),
                discriminator=self.discr, introspectables=(intr,)),
            cfg)
        return factory


@roles_provider('ptah_default_roles')
def ptah_default_roles(context, uid, registry):
    cfg = get_settings(ptah.CFG_ID_PTAH, registry)
    return cfg['default_roles']


def get_local_roles(userid, request=None,
                    context=None, get_cfg_storage=config.get_cfg_storage):
    """ calculates local roles for userid """
    if context is None:
        context = getattr(request, 'context', None)
        if context is None:
            context = getattr(request, 'root', None)

    roles = OrderedDict()

    if IOwnersAware.providedBy(context):
        if userid == context.__owner__:
            roles[Owner.id] = Allow

    for location in lineage(context):
        if ILocalRolesAware.providedBy(location):
            local_roles = location.__local_roles__
            if local_roles:
                for r in local_roles.get(userid, ()):
                    if r not in roles:
                        roles[r] = Allow

    data = []
    for r, val in roles.items():
        if val is Allow:
            data.append(r)

    registry = get_current_registry()
    for provider in get_cfg_storage(ID_ROLES_PROVIDER, registry).values():
        data.extend(provider(context, userid, registry))

    return data


DEFAULT_ACL = ACL('', 'Default ACL map')

Everyone = Role(
    'Everyone', 'Everyone', '', 'system.', True)

Authenticated = Role(
    'Authenticated', 'Authenticated', '', 'system.', True)

Owner = Role(
    'Owner', 'Owner', '', 'system.', True)

NOT_ALLOWED = Permission('__not_allowed__', 'Special permission')


def check_permission(permission, context, request=None, throw=False):
    """ Check `permission` withing `context`.

    :param permission: Permission
    :type permission: (Permission or sting)
    :param context: Context object
    :param throw: Throw HTTPForbidden exception.
    """

    if not permission or permission == NO_PERMISSION_REQUIRED:
        return True
    if permission == NOT_ALLOWED:
        if throw:
            raise HTTPForbidden()
        return False

    userid = auth_service.get_effective_userid()
    if userid == SUPERUSER_URI:
        return True

    AUTHZ = get_current_registry().getUtility(IAuthorizationPolicy)

    principals = [Everyone.id]

    if userid is not None:
        principals.extend((Authenticated.id, userid))

        roles = get_local_roles(userid, context=context)
        if roles:
            principals.extend(roles)

    res = AUTHZ.permits(context, principals, permission)

    if isinstance(res, ACLDenied):
        if throw:
            raise HTTPForbidden(res)

        return False
    return True


class PtahAuthorizationPolicy(ACLAuthorizationPolicy):

    def permits(self, context, principals, permission):
        if not permission or permission == NO_PERMISSION_REQUIRED:
            return True
        if permission == NOT_ALLOWED:
            return ACLDenied(
                '<NOT ALLOWED permission>',
                None, permission, principals, context)

        if SUPERUSER_URI in principals or \
           auth_service.get_effective_userid() == SUPERUSER_URI:
            return ACLAllowed(
                'Superuser', None, permission, principals, context)

        return super(PtahAuthorizationPolicy, self).permits(
            context, principals, permission)
