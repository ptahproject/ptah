from memphis import config


class Permissions(dict):
    pass

Permissions = Permissions()


class PermissionInfo(str):

    title = u''
    description = u''


class PermissionMap(object):

    def __init__(self, name, title, description=u''):
        self.name = name
        self.title = title
        self.description = description

        self.allowed = {}
        self.denied = {}

    def allow(self, role, *permissions):
        perms = self.allowed.setdefault(role, set())
        perms.extend(permissions)

    def deny(self, role, permissions):
        perms = self.denied.setdefault(role, set())
        perms.extend(permissions)

    @property
    def __acl__(self):
        pass


def Permission(name, title, description=u''):
    info = config.DirectiveInfo()

    permission = PermissionInfo(name)
    permission.title = title
    permission.description = description
    Permissions[str(permission)] = permission

    info.attach(
        config.Action(
            registerPermission,
            (permission,),
            discriminator = ('ptah:permission', name))
        )

    return permission


def registerPermission(perm):
    Permissions[str(perm)] = perm


View = Permission('ptah:view', 'View')
