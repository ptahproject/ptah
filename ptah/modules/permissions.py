""" security ptah module """
from zope import interface
from memphis import config, view

import ptah
from ptah import Roles
from ptah import Permissions


class IPermissionsModule(ptah.IPtahModule):
    """ module """


class PermissionsModule(ptah.PtahModule):
    __doc__ = 'Default permission settings.'

    config.utility(name='permissions')
    interface.implementsOnly(IPermissionsModule)

    name = 'permissions'
    title = 'Permissions'


class PermissionsView(view.View):
    view.pyramidView(
        'index.html', IPermissionsModule, default=True,
        template=view.template('ptah.modules:templates/permissions.pt'))

    def update(self):
        self.permissions = Permissions.values()
        self.permissions.sort(key = lambda p: p.title)

        self.roles = Roles.values()
        self.roles.sort(key = lambda r: r.title)
