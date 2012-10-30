""" base view class with access to various api's """
import cgi
import logging
from zope.interface import Interface
from pyramid.decorator import reify
from pyramid.compat import string_types, escape
from pyramid.renderers import RendererHelper
from pyramid.config.views import DefaultViewMapper

from pyramid_layer import render, tmpl_filter

import ptah.view
from ptah import config
from ptah.formatter import format

log = logging.getLogger('ptah.view')


class View(object):
    """ Base view """

    __name__ = ''
    __parent__ = None

    format = format

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


def add_message(request, msg, type='info'):
    """ Add status message

    Predefined message types

    * info

    * success

    * warning

    * error

    """
    request.session.flash(render_message(request, msg, type), 'status')


def render_message(request, msg, type='info'):
    """ Render message, return html """
    if ':' not in type:
        type = 'ptah-message:%s'%type
    return render(request, type, msg)


def render_messages(request):
    """ Render previously added messages """
    return ''.join(request.session.pop_flash('status'))


@tmpl_filter('ptah-message:error')
def error_message(context, request):
    if isinstance(context, Exception):
        context = '%s: %s'%(
            context.__class__.__name__, escape(str(context), True))

    return {'context': context}
