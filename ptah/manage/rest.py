from ptah import manage, view


@manage.module('rest')
class RestModule(manage.PtahModule):
    """
    REST Introspector
    """

    title = 'REST Introspector'


class RestModuleView(view.View):
    view.pview(
        context = RestModule,
        template = view.template('ptah.manage:templates/rest.pt'))

    def update(self):
        self.url = self.request.params.get(
            'url', '{0}/__rest__/cms/'.format(self.application_url))
