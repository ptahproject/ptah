""" This is an example of layouts """
from paste.httpserver import serve
from ptah import view, cms


class PageLayout(view.Layout):
    view.layout('page', cms.ApplicationRoot,
                layer = 'test',
                template = view.template('templates/layoutpage.pt'))

    """ override 'page' layout from ptah.cmsapp

    layer - identifier, import order does matter, last imported wins
    """

    def render(self, content, **kwargs):
        """ default implementation, just example. in most cases
        default implementation is ok. """
        if self.template is None:
            return content

        kwargs.update({'view': self,
                       'content': content,
                       'context': self.context,
                       'request': self.request,
                       'format': format})

        return self.template(**kwargs)


class WorkspaceLayout(view.Layout):
    view.layout('workspace', cms.ApplicationRoot,
                parent = 'page',
                layer = 'test',
                template = view.template('templates/layoutworkspace.pt'))

    """ same as PageLayout, it uses 'page' as parent layout """

    def update(self):
        self.user = ptah.authService.get_current_principal()
        self.isAnon = self.user is None


if __name__ == '__main__':
    """

    """
    import ptah
    app = ptah.make_wsgi_app({'settings':r'./ptah.ini'})
    serve(app, host='0.0.0.0')
