from ptah import config, view
from collections import OrderedDict
from pyramid.location import lineage
from pyramid.security import ACLDenied, Allow, Deny
from pyramid.security import ALL_PERMISSIONS, NO_PERMISSION_REQUIRED
from pyramid.interfaces import IAuthorizationPolicy
from pyramid.threadlocal import get_current_registry
from pyramid.httpexceptions import HTTPForbidden

from ptah import authService
from ptah import SUPERUSER_URI
from ptah.interfaces import IOwnersAware
from ptah.interfaces import ILocalRolesAware


ACL_ID = 'ptah:acl-map'
ROLE_ID = 'ptah:role'
PERMISSION_ID = 'ptah:permission'


def get_acls():
    return config.get_cfg_storage(ACL_ID)


def get_roles():
    return config.get_cfg_storage(ROLE_ID)


def get_permissions():
    return config.get_cfg_storage(PERMISSION_ID)


class PermissionInfo(str):

    title = u''
    description = u''


def Permission(name, title, description=u''):
    """ Register new permission. """
    info = config.DirectiveInfo()

    permission = PermissionInfo(name)
    permission.title = title
    permission.description = description

    info.attach(
        config.Action(
            lambda config, p: \
                config.get_cfg_storage(PERMISSION_ID).update({str(p): p}),
            (permission,),
            discriminator=(PERMISSION_ID, name))
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

    def __init__(self, name, title, description=u''):
        self.name = name
        self.title = title
        self.description = description

        info = config.DirectiveInfo()
        info.attach(
            config.Action(
                lambda config, p: \
                    config.get_cfg_storage(ACL_ID).update({name: p}),
                (self,),
                discriminator=('ptah:acl-map', name))
            )
        self.directiveInfo = info

    def get(self, typ, role):
        for r in self:
            if r[0] == typ and r[1] == role:
                return r

        return None

    def allow(self, role, *permissions):
        """ Give permissions to role """

        if not isinstance(role, basestring):
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

        if not isinstance(role, basestring):
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

    def __init__(self, acls):
        self.acls = acls

    def __iter__(self):
        acls = config.get_cfg_storage(ACL_ID)
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
        info.attach(
            config.Action(
                lambda config, r: \
                    config.get_cfg_storage(ROLE_ID).update({r.name: r}),
                (self, ),
                discriminator=(ROLE_ID, name))
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


def get_local_roles(userid, request=None, context=None):
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

    userid = authService.get_userid()
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

view.set_checkpermission(check_permission)


@config.cleanup
def cleanup():
    DEFAULT_ACL[:] = []
