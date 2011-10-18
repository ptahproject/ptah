""" app management module """
import ptah
from ptah import view, form
from pyramid.httpexceptions import HTTPFound


class ApplicationsModule(ptah.PtahModule):
    __doc__ = 'Ptah CMS Applications management.'

    title = 'Ptah CMS Applications'
    ptah.manageModule('ptah-apps')

    def __getitem__(self, key):
        f = ptah.cms.Factories[key]
        return AppFactory(f, self, self.request)


class ApplicationsModuleView(view.View):
    view.pyramidview(
        context=ApplicationsModule,
        template=view.template('ptah.cmsapp:templates/module-apps.pt'))

    def update(self):
        factories = []
        for factory in ptah.cms.Factories.values():
            factories.append((factory.title, factory))

        factories.sort()
        self.factories = [f for _t, f in factories]


class AppFactory(object):

    def __init__(self, factory, context, request):
        self.__name__ = factory.id
        self.__parent__ = context
        self.request = request
        self.factory = factory
        self.root = factory(request)


class SharingForm(form.Form):
    view.pyramidview(
        context = AppFactory,
        template = view.template('ptah.cmsapp:templates/module-apps-sharing.pt'))

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
        return {'term': self.request.session.get('sharing-term', '')}

    def get_principal(self, id):
        return ptah.resolve(id)

    def update(self):
        super(SharingForm, self).update()

        request = self.request
        context = self.context.root

        self.roles = [r for r in ptah.Roles.values() if not r.system]
        self.local_roles = local_roles = context.__local_roles__

        term = request.session.get('sharing-term', '')
        if term:
            self.users = list(ptah.search_principals(term))

        if 'form.buttons.save' in request.POST:
            users = []
            userdata = {}
            for attr, val in request.POST.items():
                if attr.startswith('user-'):
                    userId, roleId = attr.split('-')[1:]
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

        self.request.session['sharing-term'] = data['term']
        raise HTTPFound(location = self.request.url)


class TypeIntrospection(object):
    """ Ptah CMS content types """

    name = 'ptah-cms:type'
    title = 'Content Types'
    ptah.introspection('ptah-cms:type')

    actions = view.template('ptah.cmsapp:templates/directive-type.pt')

    def __init__(self, request):
        self.request = request

    def renderAction(self, action):
        pass

    def renderActions(self, *actions):
        return self.actions(
            types = ptah.cms.Types,
            actions = actions,
            request = self.request)
