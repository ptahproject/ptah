import ptah
from pyramid.view import view_config
from pyramid.interfaces import IRouteRequest


@ptah.manage.module('rest')
class RestModule(ptah.manage.PtahModule):
    """
    REST Introspector
    """

    title = 'REST Introspector'

    def available(self):
        """ check if ptah rest api is enabled """
        return self.request.registry.queryUtility(
            IRouteRequest, 'ptah-rest') is not None


@view_config(
    context=RestModule,
    wrapper=ptah.wrap_layout(),
    renderer='ptah.manage:templates/rest.pt')

class RestModuleView(ptah.View):

    def update(self):
        self.url = self.request.params.get(
            'url', '{0}/__rest__/cms/'.format(self.application_url))
