""" simple messages """
from pyramid.compat import escape, string_types
from ptah.renderer import render


def add_message(request, msg, type='info'):
    """ Add status message

    Predefined message types

    * info

    * success

    * warning

    * error

    """
    if ':' not in type:
        type = 'message:%s'%type

    request.session.flash(render(request, type, msg), 'status')


def render_messages(request):
    """ Render previously added messages """
    return ''.join(request.session.pop_flash('status'))

def error_message(context, request):
    """ Error message filter """
    if not isinstance(context, (set, list, tuple)):
        context = (context,)

    errors = []
    for err in context:
        if isinstance(err, Exception):
            err = '%s: %s'%(
                err.__class__.__name__, escape(str(err), True))
        errors.append(err)

    return {'errors': errors}


def includeme(config):
    config.include('pyramid_chameleon')
    config.include('ptah.renderer')

    config.add_layer('message', path='ptah.message:templates/')

    config.add_request_method(add_message, 'add_message')
    config.add_request_method(render_messages, 'render_messages')

    config.add_tmpl_filter('message:error', error_message)
