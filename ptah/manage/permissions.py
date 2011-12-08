""" security ptah module """
import ptah
from ptah import view, manage
from ptah.manage import module, intr_renderer, get_manage_url


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
        self.manage = get_manage_url(self.request)
        self.permissions = sorted(ptah.get_permissions().values(),
                                  key = lambda p: p.title)

        acls = ptah.get_acls()
        self.acls = sorted([acl for acl in acls.values() if acl.id != ''],
                           key = lambda a: a.title)
        self.acls.insert(0, ptah.DEFAULT_ACL)


class RolesView(view.View):
    view.pview(
        'roles.html', PermissionsModule,
        template=view.template('ptah.manage:templates/roles.pt'))

    def update(self):
        self.roles = sorted(ptah.get_roles().values(),
                            key = lambda r: r.title)
