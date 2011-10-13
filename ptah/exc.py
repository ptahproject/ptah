""" forbidden view """
import urllib
from memphis import view
from pyramid.httpexceptions import HTTPFound, HTTPForbidden, HTTPNotFound

from ptah import authService
from ptah.manage import DefaultRoot
from ptah.mail import MAIL
from ptah.settings import PTAH_CONFIG


view.registerLayout(
    'ptah-exception', parent='.',
    template = view.template('ptah:templates/ptah-exception.pt'))


class Forbidden(view.View):
    view.pyramidView(context=HTTPForbidden,
                     layout='ptah-exception',
                     template=view.template('ptah:templates/forbidden.pt'))

    def update(self):
        request = self.request

        context = getattr(request, 'context', None)
        if context is None:
            context = getattr(request, 'root', None)

        self.__parent__ = context

        user = authService.get_userid()
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
        context = getattr(self.request, 'context', None)
        if context is None:
            context = getattr(self.request, 'root', None)

        self.__parent__ = context

        self.admin = MAIL.from_name
        self.email = MAIL.from_address
        self.request.response.status = HTTPNotFound.code
