""" security ptah module """
from pyramid.view import view_config
import ptah
from ptah import view, manage
from ptah.manage import module, intr_renderer, get_manage_url


@module('permissions')
class PermissionsModule(manage.PtahModule):
    __doc__ = 'A listing of all permission sets and their definitions'

    title = 'Permissions'


@view_config(
    context=PermissionsModule, wrapper=ptah.wrap_layout(),
    renderer='ptah.manage:templates/permissions.pt')
class PermissionsView(view.View):
    """ Permissions module default view """

    def update(self):
        self.manage = get_manage_url(self.request)
        self.permissions = sorted(ptah.get_permissions().values(),
                                  key = lambda p: p.title)

        acls = ptah.get_acls()
        self.acls = sorted([acl for acl in acls.values() if acl.id != ''],
                           key = lambda a: a.title)
        self.acls.insert(0, ptah.DEFAULT_ACL)


@view_config(
    'roles.html',
    context=PermissionsModule,
    wrapper=ptah.wrap_layout(),
    renderer='ptah.manage:templates/roles.pt')

class RolesView(view.View):
    """ Roles view for permissions manage module """

    def update(self):
        self.roles = sorted(ptah.get_roles().values(), key = lambda r: r.title)
