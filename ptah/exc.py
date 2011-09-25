""" forbidden view """
import urllib
from memphis import view, config
from pyramid.interfaces import IRootFactory
from pyramid.traversal import DefaultRootFactory
from pyramid.httpexceptions import HTTPFound, HTTPForbidden, HTTPNotFound

from ptah import authService
from ptah.manage import DefaultRoot
from ptah.mail import MAIL
from ptah.settings import PTAH_CONFIG


view.registerLayout(
    'ptah-exception', parent='.',
    template = view.template('ptah:templates/ptah-exception.pt'))

ROOT_FACTORY = None

@config.handler(config.SettingsInitialized)
def initRootFactory(ev):
    global ROOT_FACTORY
    ROOT_FACTORY = config.registry.queryUtility(
        IRootFactory, default=DefaultRootFactory)


class Forbidden(view.View):
    view.pyramidView(context=HTTPForbidden,
                     layout='ptah-exception',
                     template=view.template('ptah:templates/forbidden.pt'))

    def update(self):
        request = self.request

        self.__parent__ = ROOT_FACTORY(request)

        user = authService.getUserId()
        if user is None:
            loginurl = PTAH_CONFIG.login
            if loginurl and not loginurl.startswith(('http://', 'https://')):
                loginurl = request.application_url + loginurl
            else:
                loginurl = request.application_url + '/login.html'

            location = '%s?%s'%(
                loginurl, urllib.urlencode({'came_from': request.url}))
            if isinstance(location, unicode):
                location = location.encode('utf-8')

            request.response.status = HTTPFound.code
            request.response.headers['location'] = location
            return

        self.request.response.status = HTTPForbidden.code


class NotFound(view.View):
    view.pyramidView(context=HTTPNotFound,
                     layout='ptah-exception',
                     template=view.template('ptah:templates/notfound.pt'))

    def update(self):
        self.__parent__ = ROOT_FACTORY(self.request)

        self.admin = MAIL.from_name
        self.email = MAIL.from_address
        self.request.response.status = HTTPNotFound.code
