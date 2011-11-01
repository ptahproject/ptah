from ptah import manage, view


class RestModule(manage.PtahModule):
    """
    REST Introspector
    """

    title = 'REST Introspector'
    manage.module('rest')


class RestModuleView(view.View):
    view.pview(
        context = RestModule,
        template = view.template('ptah.manage:templates/rest.pt'))

    def update(self):
        self.appurl = self.request.application_url
        self.url = self.request.get('url', '%s/__rest__/cms/' % self.appurl)
