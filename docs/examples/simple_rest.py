""" This is an example of useing form (imperative style). """
from paste.httpserver import serve

import ptah
from ptah import cms
from ptah.cms import restaction, View, ModifyContent


@restaction('extra-info', ptah_cms.Content, permission=View)
def extraInfo(content, request):
    """ __doc__ is used for action description """

    return {'title': content.title,
            'email': 'ptah@ptahproject.org',
            'message': 'Ptah rest api'}


@restaction('protected-info', ptah_cms.Content, permission=ModifyContent)
def protectedInfo(content, request):
    """ protected rest action """

    return {'title': content.title,
            'email': 'ptah@ptahproject.org',
            'message': 'Ptah rest api'}


if __name__ == '__main__':
    """ ...

    """
    app = ptah.make_wsgi_app({'settings':r'./ptah.ini'})
    serve(app, host='0.0.0.0')
