from memphis import config


class Permissions(dict):
    pass

Permissions = Permissions()


class PermissionInfo(str):

    title = ''
    description = ''
        

def Permission(name, title, description=u''):
    info = config.DirectiveInfo()

    permission = PermissionInfo(name)
    permission.title = title
    permission.description = description

    info.attach(
        config.Action(
            registerPermission,
            (permission,),
            discriminator = ('ptah:permission', name))
        )

    return permission


def registerPermission(perm):
    Permissions[str(perm)] = perm
