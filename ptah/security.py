from memphis import config
from collections import OrderedDict
from pyramid.location import lineage
from pyramid.security import Allow, Deny, ALL_PERMISSIONS

from ptah.interfaces import IOwnersAware
from ptah.interfaces import ILocalRolesAware

ACLs = {}
Roles = {}
Permissions = {}


class PermissionInfo(str):

    title = u''
    description = u''


def Permission(name, title, description=u''):
    info = config.DirectiveInfo()

    permission = PermissionInfo(name)
    permission.title = title
    permission.description = description
    Permissions[str(permission)] = permission

    info.attach(
        config.Action(
            lambda p: Permissions.update({str(p): p}),
            (permission,), discriminator = ('ptah:permission', name))
        )

    return permission


class ACL(list):

    # do we need somthing like Unset, to unset permission from parent

    def __init__(self, name, title, description=u''):
        self.name = name
        self.title = title
        self.description = description

        ACLs[name] = self

        info = config.DirectiveInfo()
        info.attach(
            config.Action(
                lambda p: ACLs.update({name: p}),
                (self,), discriminator = ('ptah:acl-map', name))
            )

    def get(self, typ, role):
        for r in self:
            if r[0] == typ and r[1] == role:
                return r

        return None

    def allow(self, role, *permissions):
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
        for aname in self.acls:
            acl = ACLs.get(aname)
            if acl is not None:
                for rec in acl:
                    yield rec


class ACLsProperty(object):

    def __get__(self, inst, klass):
        acls = getattr(inst, '__acls__', ())
        if acls:
            return ACLsMerge(acls)
        else:
            return ()


class Role(object):

    def __init__(self, name, title, description='',
                 prefix='role:', system=False):
        id = '%s%s'%(prefix, name)

        self.id = id
        self.name = name
        self.title = title
        self.description = description
        self.system = system

        self.allowed = set()
        self.denied = set()

        # register role
        Roles[name] = self

        # conflict detection and introspection
        info = config.DirectiveInfo()
        info.attach(
            config.Action(
                lambda r: Roles.update({r.name: r}),
                (self,), discriminator = ('ptah:role', name))
            )

    def __str__(self):
        return 'Role<%s>'%self.title

    def __repr__(self):
        return self.id

    def allow(self, *permissions):
        DEFAULT_ACL.allow(self.id, *permissions)

    def deny(self, *permissions):
        DEFAULT_ACL.deny(self.id, *permissions)

    def unset(self, *permissions):
        DEFAULT_ACL.unset(self.id, *permissions)


def LocalRoles(userid, request=None, context=None):
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

View = Permission('ptah:view', 'View')

Everyone = Role(
    'Everyone', 'Everyone', '', 'system.', True)
Everyone.allow(View)

Authenticated = Role(
    'Authenticated', 'Authenticated', '', 'system.', True)

Owner = Role(
    'Owner', 'Owner', '', 'system.', True)


@config.addCleanup
def cleanup():
    DEFAULT_ACL[:] = []
    ACLs.clear()
    Roles.clear()
    Permissions.clear()
