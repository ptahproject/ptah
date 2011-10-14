""" security ptah module """
from zope import interface
from memphis import config, view

import ptah
from ptah import Roles
from ptah import Permissions


class PermissionsModule(ptah.PtahModule):
    __doc__ = 'Default permission settings.'

    title = 'Permissions'
    ptah.manageModule('permissions')


view.register_snippet(
    'ptah-module-actions', PermissionsModule,
    template = view.template('ptah_modules:templates/permissions-actions.pt'))


class PermissionsView(view.View):
    view.pyramidView(
        context=PermissionsModule,
        template=view.template('ptah_modules:templates/permissions.pt'))

    def update(self):
        self.permissions = Permissions.values()
        self.permissions.sort(key = lambda p: p.title)

        self.acls = [acl for acl in ptah.ACLs.values() if acl.name != '']
        self.acls.sort(key = lambda a: a.title)
        self.acls.insert(0, ptah.DEFAULT_ACL)


class RolesView(view.View):
    view.pyramidView(
        'roles.html', PermissionsModule,
        template=view.template('ptah_modules:templates/roles.pt'))

    def update(self):
        self.roles = Roles.values()
        self.roles.sort(key = lambda r: r.title)


class RoleIntrospection(object):
    """ Role registrations """

    title = 'Role'
    ptah.introspection('ptah:role')

    actions = view.template('ptah_modules:templates/directive-role.pt')

    def __init__(self, request):
        self.request = request

    def renderAction(self, action):
        pass

    def renderActions(self, *actions):
        return self.actions(
            roles = ptah.Roles,
            actions = actions,
            request = self.request)


class PermissionIntrospection(object):
    """ Permission registrations """

    title = 'Permission'
    ptah.introspection('ptah:permission')

    actions = view.template('ptah_modules:templates/directive-permission.pt')

    def __init__(self, request):
        self.request = request

    def renderAction(self, action):
        pass

    def renderActions(self, *actions):
        return self.actions(
            permissions = ptah.Permissions,
            actions = actions,
            request = self.request)
