""" app management module """
import ptah
from ptah import view, form, manage, cms
from pyramid.httpexceptions import HTTPFound


class ApplicationsModule(manage.PtahModule):
    __doc__ = u'A listing of all registered Ptah Applications.'

    title = 'Applications'
    manage.module('apps')

    def __getitem__(self, key):
        for id, factory in cms.get_app_factories().items():
            if factory.name == key:
                return AppFactory(factory, self, self.request)

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


class AppFactory(object):

    def __init__(self, factory, context, request):
        self.__name__ = factory.id
        self.__parent__ = context
        self.request = request
        self.factory = factory
        self.app = factory(request)


class SharingForm(form.Form):
    view.pview(
        context = AppFactory,
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
        context = self.context.app

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
