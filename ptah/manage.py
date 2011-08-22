""" user management """
from zope import interface
from zope.component import getUtility, getUtilitiesFor
from webob.exc import HTTPForbidden
from memphis import view
from ptah.models import User
from ptah.settings import PTAH
from ptah.interfaces import IAuthentication
from ptah.interfaces import IPtahUser, IPtahManageRoute
from ptah.interfaces import IManageUserAction, IManageAction


class PtahUser(object):
    interface.implements(IPtahUser)

    def __init__(self, user, parent):
        self.user = user
        self.__name__ = str(user.id)
        self.__parent__ = parent


class PtahManageRoute(object):
    interface.implements(IPtahManageRoute)

    __name__ = 'ptah-manage'
    __parent__ = view.DefaultRoot()

    def __init__(self, request):
        self.request = request
        
        login = getUtility(IAuthentication).getCurrentLogin()
        if login and login in PTAH.managers:
            pass

        raise HTTPForbidden()

    def __getitem__(self, key):
        try:
            uid = int(key)
        except:
            raise KeyError(key)

        user = User.getById(uid)
        if user is None:
            raise KeyError(key)

        return PtahUser(user, self)


view.registerRoute(
    'ptah-manage', '/ptah-manage/*traverse', PtahManageRoute)


class PtahManageLayout(view.Layout):
    view.layout(
        '', IPtahManageRoute, parent='.',
        template = view.template('ptah.views:ptah-manage.pt'))

    actions = ()
    user = None

    def update(self):
        self.url = self.request.route_url('ptah-manage', traverse='')

        actions = []

        if IPtahManageRoute.providedBy(self.view.context):
            for name, util in getUtilitiesFor(IManageAction):
                if util.available():
                    actions.append((util.title, util))

        elif IPtahUser.providedBy(self.view.context):
            self.url = '%s%s/'%(self.url, self.view.context.__name__)
            self.user = self.view.context.user.name
            for name, util in getUtilitiesFor(IManageUserAction):
                if util.available(self.view.context.user):
                    actions.append((util.title, util))

        actions.sort()
        self.actions = [a for t, a in actions]
