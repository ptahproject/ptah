""" simple messages """
from pyramid.compat import escape, string_types
from ptah.renderer import render, tmpl_filter


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


@tmpl_filter('message:error')
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
