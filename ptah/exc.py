""" forbidden view """
import urllib
from ptah import view
from pyramid.httpexceptions import HTTPFound, HTTPForbidden, HTTPNotFound

import ptah
from ptah import authService
from ptah.mail import MAIL
from ptah.settings import PTAH_CONFIG


class LayoutPage(view.Layout):
    view.layout('ptah-page',
                template=view.template("ptah:templates/ptah-page.pt"))

    def update(self):
        self.root = getattr(self.request, 'root', None)
        self.user = authService.get_current_principal()
        self.isanon = self.user is None
        self.ptahmanager = ptah.get_access_manager()(authService.get_userid())


class Forbidden(view.View):
    view.pview(context=HTTPForbidden, layout='ptah-page',
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
            elif not loginurl:
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
    view.pview(context=HTTPNotFound, layout='ptah-page',
               template=view.template('ptah:templates/notfound.pt'))

    def update(self):
        context = getattr(self.request, 'context', None)
        if context is None:
            context = getattr(self.request, 'root', None)

        self.__parent__ = context

        self.admin = MAIL.from_name
        self.email = MAIL.from_address
        self.request.response.status = HTTPNotFound.code
