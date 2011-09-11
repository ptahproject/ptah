""" forbidden view """
import urllib
from webob.exc import HTTPFound, HTTPForbidden
from pyramid.security import authenticated_userid

from memphis import view
from ptah.settings import PTAH


view.registerLayout(
    'ptah-exception', parent='.',
    template = view.template('ptah:templates/ptah-exception.pt'))


class Forbidden(view.View):
    view.pyramidView(context=HTTPForbidden,
                     layout='ptah-exception',
                     template=view.template('ptah:templates/forbidden.pt'))

    def update(self):
        self.__parent__ = view.DefaultRoot()

        request = self.request

        user = authenticated_userid(request)
        if user is None:
            loginurl = PTAH.login
            if loginurl and not loginurl.startswith(('http://', 'https://')):
                loginurl = request.application_url + loginurl
            else:
                loginurl = request.application_url + '/login.html'

            request.response.status = HTTPFound.code
            request.response.headers['location'] = '%s?%s'%(
                loginurl, urllib.urlencode({'came_from': request.url}))
            return

        self.request.response.status = HTTPForbidden.code
