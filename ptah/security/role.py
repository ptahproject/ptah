from memphis import config
from collections import OrderedDict
from pyramid.location import lineage
from pyramid.security import Allow, Deny, ALL_PERMISSIONS

from interfaces import IOwnersAware
from interfaces import ILocalRolesAware


class Roles(dict):
    pass

Roles = Roles()


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
        if self.allowed is ALL_PERMISSIONS:
            return

        if ALL_PERMISSIONS in permissions:
            self.allowed = ALL_PERMISSIONS
            return

        for perm in permissions:
            self.allowed.add(perm)

    def deny(self, *permissions):
        if self.denied is ALL_PERMISSIONS:
            return

        if ALL_PERMISSIONS in permissions:
            self.denied = ALL_PERMISSIONS
            return

        for perm in permissions:
            self.denied.add(perm)

    def unset(self, *permissions):
        if ALL_PERMISSIONS in permissions:
            self.denied = set()
            self.allowed = set()
            return

        for perm in permissions:
            if self.allowed is not ALL_PERMISSIONS and perm in self.allowed:
                self.allowed.remove(perm)
            if self.denied is not ALL_PERMISSIONS and perm in self.denied:
                self.denied.remove(perm)


Everyone = Role(
    'Everyone', 'Everyone', '', 'system.', True)

Authenticated = Role(
    'Authenticated', 'Authenticated', '', 'system.', True)

Owner = Role(
    'Owner', 'Owner', '', 'system.', True)


def LocalRoles(userid, request=None, context=None):
    if context is None:
        context = getattr(request, 'context', None)
        if context is None:
            context = getattr(request, 'root', None)

    roles = OrderedDict()

    if IOwnersAware.providedBy(context):
        if userid in context.__owners__:
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


ACL = []

@config.handler(config.SettingsInitialized)
def initialized(ev):
    global ACL

    for role in Roles.values():
        if role.denied:
            ACL.append((Deny, role.id, role.denied))
        if role.allowed:
            ACL.append((Allow, role.id, role.allowed))


@config.addCleanup
def cleanup():
    ACL[:] = []
    Roles.clear()
