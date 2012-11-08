""" base view class with access to various api's """
import logging
from pyramid.decorator import reify

import ptah

log = logging.getLogger('ptah.view')


class View(object):
    """ Base view """

    __name__ = ''
    __parent__ = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.__parent__ = context

    @reify
    def application_url(self):
        url = self.request.application_url
        if url.endswith('/'):
            url = url[:-1]
        return url

    def update(self):
        return {}

    def __call__(self):
        result = self.update()
        if result is None:
            result = {}

        return result


class MasterLayout(View):

    @reify
    def user(self):
        userid = ptah.auth_service.get_userid()
        return ptah.resolve(userid)

    @reify
    def manage_url(self):
        return ptah.manage.get_manage_url(self.request)

    @reify
    def actions(self):
        return []
