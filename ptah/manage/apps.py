""" app management module """
import ptah
from ptah import view, form, cms
from pyramid.httpexceptions import HTTPFound
from pyramid.interfaces import IRequest, IRouteRequest

from ptah.manage import manage

MANAGE_APP_ROUTE = MANAGE_APP_CATEGORY = 'ptah-manage-app'

view.register_route(MANAGE_APP_ROUTE, '!~~~~~~~~~~~~~', use_global_views=False)


class ApplicationsModule(manage.PtahModule):
    __doc__ = u'A listing of all registered Ptah Applications.'

    title = 'Applications'
    manage.module('apps')

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


class ApplicationsModuleView(view.View):
    view.pview(
        context=ApplicationsModule,
        template=view.template('ptah.manage:templates/apps.pt'))

    def update(self):
        factories = []
        for factory in cms.get_app_factories().values():
            factories.append((factory.title, factory))

        factories.sort()
        self.factories = [f for _t, f in factories]


class AppLayout(manage.LayoutManage):
    view.layout('ptah-manage', manage.PtahManageRoute,
                route=MANAGE_APP_ROUTE,
                template=view.template("ptah.manage:templates/ptah-manage.pt"))


class AppContentLayout(view.Layout):
    view.layout('', cms.Node,
                parent="ptah-manage",
                route=MANAGE_APP_ROUTE,
                template=view.template("templates/apps-layout.pt"))

    def update(self):
        self.actions = ptah.list_uiactions(
            self.context, self.request, MANAGE_APP_CATEGORY)


class ViewForm(form.DisplayForm):
    view.pview(
        context=cms.Content,
        route=MANAGE_APP_ROUTE,
        template=view.template("templates/apps-contentview.pt"))

    @property
    def fields(self):
        return self.context.__type__.fieldset

    def form_content(self):
        data = {}
        for name, field in self.context.__type__.fieldset.items():
            data[name] = getattr(self.context, name, field.default)

        return data


class SharingForm(form.Form):
    view.pview(
        'sharing.html',
        context = cms.IContent,
        route = MANAGE_APP_ROUTE,
        template = view.template('ptah.manage:templates/apps-sharing.pt'))

    csrf = True
    fields = form.Fieldset(
        form.FieldFactory(
            'text',
            'term',
            title = u'Search term',
            description = 'Searches users by login and email',
            missing = u'',
            default = u'')
        )


    users = None
    bsize = 15

    def form_content(self):
        return {'term': self.request.session.get('apps-sharing-term', '')}

    def get_principal(self, id):
        return ptah.resolve(id)

    def update(self):
        super(SharingForm, self).update()

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

    @form.button('Search', actype=form.AC_PRIMARY)
    def search(self):
        data, error = self.extract()

        if not data['term']:
            self.message('Please specify search term', 'warning')
            return

        self.request.session['apps-sharing-term'] = data['term']
        raise HTTPFound(location = self.request.url)


ptah.uiaction(
    ptah.ILocalRolesAware, **{'id': 'sharing',
                              'title': 'Sharing',
                              'action': 'sharing.html',
                              'category': MANAGE_APP_CATEGORY,
                              'sort_weight': 10.0})
