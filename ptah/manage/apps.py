""" app management module """
import ptah
from ptah import view, form, cms
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.interfaces import IRequest, IRouteRequest

from ptah.manage import manage

MANAGE_APP_ROUTE = MANAGE_APP_CATEGORY = 'ptah-manage-app'


@manage.module('apps')
class ApplicationsModule(manage.PtahModule):
    __doc__ = 'A listing of all registered Ptah Applications.'

    title = 'Applications'

    def __getitem__(self, key):
        for id, factory in cms.get_app_factories().items():
            if factory.name == key:
                request = self.request
                request.request_iface = request.registry.getUtility(
                    IRouteRequest, name=MANAGE_APP_ROUTE)
                request.app_factory = factory
                app = factory()
                app.__parent__ = self
                app.__root_path__ = '/ptah-manage/apps/%s/'%app.__name__
                return app

        raise KeyError(key)

    def available(self):
        return bool(cms.get_app_factories())


@view_config(
    context=ApplicationsModule, wrapper=ptah.wrap_layout(),
    renderer='ptah.manage:templates/apps.pt')

class ApplicationsModuleView(ptah.View):
    """ Applications module default view """

    def update(self):
        factories = []
        for factory in cms.get_app_factories().values():
            factories.append((factory.title, factory))

        self.factories = [f for _t, f in sorted(factories)]


@ptah.layout(
    'ptah-manage', manage.PtahManageRoute,
    route_name=MANAGE_APP_ROUTE,
    renderer="ptah.manage:templates/ptah-manage.pt")

class AppLayout(manage.LayoutManage):
    """ Application module layout """


@ptah.layout(
    '', cms.Node, parent="ptah-manage",
    route_name=MANAGE_APP_ROUTE,
    renderer="ptah.manage:templates/apps-layout.pt")

class AppContentLayout(ptah.View):
    """ Application module content layout """

    def update(self):
        self.actions = ptah.list_uiactions(
            self.context, self.request, MANAGE_APP_CATEGORY)


@view_config(
    context=cms.Content,
    wrapper=ptah.wrap_layout(),
    route_name=MANAGE_APP_ROUTE,
    renderer="ptah.manage:templates/apps-contentview.pt")

class ViewForm(form.DisplayForm):

    @property
    def fields(self):
        return self.context.__type__.fieldset

    def form_content(self):
        data = {}
        for name, field in self.context.__type__.fieldset.items():
            data[name] = getattr(self.context, name, field.default)

        return data


@view_config(
    'sharing.html',
    context=cms.IContent,
    route_name=MANAGE_APP_ROUTE, wrapper=ptah.wrap_layout(),
    renderer='ptah.manage:templates/apps-sharing.pt')

class SharingForm(form.Form):
    """ Sharing form """

    csrf = True
    fields = form.Fieldset(
        form.FieldFactory(
            'text',
            'term',
            title = 'Search term',
            description = 'Searches users by login and email',
            missing = '',
            default = '')
        )


    users = None
    bsize = 15

    def form_content(self):
        return {'term': self.request.session.get('apps-sharing-term', '')}

    def get_principal(self, id):
        return ptah.resolve(id)

    def update(self):
        res = super(SharingForm, self).update()

        request = self.request
        context = self.context

        self.roles = [r for r in ptah.get_roles().values() if not r.system]
        self.local_roles = local_roles = context.__local_roles__

        term = request.session.get('apps-sharing-term', '')
        if term:
            self.users = list(ptah.search_principals(term))

        if 'form.buttons.save' in request.POST:
            users = []
            userdata = {}
            for attr, val in request.POST.items():
                if attr.startswith('user-'):
                    userId, roleId = attr[5:].rsplit('-',1)
                    data = userdata.setdefault(str(userId), [])
                    data.append(str(roleId))
                if attr.startswith('userid-'):
                    users.append(str(attr.split('userid-')[-1]))

            for uid in users:
                if userdata.get(uid):
                    local_roles[str(uid)] = userdata[uid]
                elif uid in local_roles:
                    del local_roles[uid]

            context.__local_roles__ = local_roles

        return res

    @form.button('Search', actype=form.AC_PRIMARY)
    def search(self):
        data, error = self.extract()

        if not data['term']:
            self.message('Please specify search term', 'warning')
            return

        self.request.session['apps-sharing-term'] = data['term']
        return HTTPFound(location = self.request.url)


ptah.uiaction(
    ptah.ILocalRolesAware, **{'id': 'view',
                              'title': 'View',
                              'action': '',
                              'category': MANAGE_APP_CATEGORY,
                              'sort_weight': 1.0})

ptah.uiaction(
    ptah.ILocalRolesAware, **{'id': 'sharing',
                              'title': 'Sharing',
                              'action': 'sharing.html',
                              'category': MANAGE_APP_CATEGORY,
                              'sort_weight': 10.0})
