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


view.registerPagelet(
    'ptah-module-actions', PermissionsModule,
    template = view.template('ptah.modules:templates/permissions-actions.pt'))


class PermissionsView(view.View):
    view.pyramidView(
        'index.html', PermissionsModule, default=True,
        template=view.template('ptah.modules:templates/permissions.pt'))

    def update(self):
        self.permissions = Permissions.values()
        self.permissions.sort(key = lambda p: p.title)

        self.acls = [acl for acl in ptah.ACLs.values() if acl.name != '']
        self.acls.sort(key = lambda a: a.title)
        self.acls.insert(0, ptah.DEFAULT_ACL)


class RolesView(view.View):
    view.pyramidView(
        'roles.html', PermissionsModule,
        template=view.template('ptah.modules:templates/roles.pt'))

    def update(self):
        self.roles = Roles.values()
        self.roles.sort(key = lambda r: r.title)
