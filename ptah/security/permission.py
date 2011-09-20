from zope import interface
from memphis import config
from pyramid.security import Allow, Deny
from ptah.security.interfaces import IPermissionsMapAware


class _Permissions(dict):
    pass

Permissions = _Permissions()
PermissionsMaps = _Permissions()


class PermissionInfo(str):

    title = u''
    description = u''


class PermissionsMap(object):

    # do we need somthing like Unset, to unset permission from parent

    def __init__(self, name, title, description=u''):
        self.name = name
        self.title = title
        self.description = description

        self.allowed = {}
        self.denied = {}

        PermissionsMaps[name] = self

        info = config.DirectiveInfo()
        info.attach(
            config.Action(
                lambda p: PermissionsMaps.update({name: p}),
                (self,), discriminator = ('ptah:permission-map', name))
            )

    def allow(self, role, *permissions):
        if not isinstance(role, basestring):
            role = role.id
            
        perms = self.allowed.setdefault(role, set())
        perms.update(permissions)

    def deny(self, role, *permissions):
        if not isinstance(role, basestring):
            role = role.id

        perms = self.denied.setdefault(role, set())
        perms.update(permissions)


class PermissionsMapSupport(object):
    interface.implements(IPermissionsMapAware)

    __permissions__ = []

    def _acl_(self):
        acl = []

        for name in self.__permissions__:
            pmap = PermissionsMaps.get(name)
            if pmap:
                acl.extend(
                    [(Allow, role, permissions) 
                     for role, permissions in pmap.denied.items()])

        for name in self.__permissions__:
            pmap = PermissionsMaps.get(name)
            if pmap:
                acl.extend(
                    [(Allow, role, permissions) 
                     for role, permissions in pmap.allowed.items()])

        return acl

    __acl__ = property(_acl_)


def Permission(name, title, description=u''):
    info = config.DirectiveInfo()

    permission = PermissionInfo(name)
    permission.title = title
    permission.description = description
    Permissions[str(permission)] = permission

    info.attach(
        config.Action(
            lambda p: Permissions.update({str(p): p}),
            (permission,),
            discriminator = ('ptah:permission', name))
        )

    return permission


View = Permission('ptah:view', 'View')
