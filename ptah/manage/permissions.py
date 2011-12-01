""" security ptah module """
import ptah
from ptah import view, manage
from ptah.manage import module, intr_renderer


@module('permissions')
class PermissionsModule(manage.PtahModule):
    __doc__ = 'A listing of all permission sets and their definitions'

    title = 'Permissions'


view.register_snippet(
    'ptah-module-actions', PermissionsModule,
    template = view.template('ptah.manage:templates/permissions-actions.pt'))


class PermissionsView(view.View):
    view.pview(
        context=PermissionsModule,
        template=view.template('ptah.manage:templates/permissions.pt'))

    def update(self):
        self.manage_url = manage.CONFIG.manage_url
        self.permissions = sorted(ptah.get_permissions().values(),
                                  key = lambda p: p.title)

        acls = ptah.get_acls()
        self.acls = sorted([acl for acl in acls.values() if acl.name != ''],
                           key = lambda a: a.title)
        self.acls.insert(0, ptah.DEFAULT_ACL)


class RolesView(view.View):
    view.pview(
        'roles.html', PermissionsModule,
        template=view.template('ptah.manage:templates/roles.pt'))

    def update(self):
        self.roles = sorted(ptah.get_roles().values(),
                            key = lambda r: r.title)


@intr_renderer('ptah:role')
class RoleIntrospection(object):
    """ Role registrations """

    title = 'Role'

    actions = view.template('ptah.manage:templates/directive-role.pt')

    def __init__(self, request):
        self.request = request

    def renderActions(self, *actions):
        return self.actions(
            roles = ptah.get_roles(),
            actions = actions,
            manage_url = manage.CONFIG.manage_url,
            request = self.request)


@intr_renderer('ptah:permission')
class PermissionIntrospection(object):
    """ Permission registrations """

    title = 'Permission'

    actions = view.template('ptah.manage:templates/directive-permission.pt')

    def __init__(self, request):
        self.request = request

    def renderActions(self, *actions):
        return self.actions(
            actions = actions,
            manage_url = manage.CONFIG.manage_url,
            request = self.request)
