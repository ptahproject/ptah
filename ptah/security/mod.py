""" security ptah module """
import ptah
from zope import interface
from memphis import config, view

from role import Roles
from permission import Permissions


class ISecurityModule(ptah.IPtahModule):
    """ module """


class SecurityModule(ptah.PtahModule):
    """ Security info module. """

    config.utility(name='security')
    interface.implementsOnly(ISecurityModule)

    name = 'security'
    title = 'Security'
    description = 'Various security related info.'


class PermissionsView(view.View):
    view.pyramidView(
        'index.html', ISecurityModule, default=True, layout='',
        template=view.template('ptah.security:templates/permissions.pt'))

    def update(self):
        self.permissions = Permissions.values()
        self.permissions.sort(key = lambda p: p.title)

        self.roles = Roles.values()
        self.roles.sort(key = lambda r: r.title)
