import ptah
from ptah import cms, view, form
from pyramid.httpexceptions import HTTPFound


class SharingForm(form.Form):
    view.pview(
        'sharing.html', ptah.ILocalRolesAware,
        permission = cms.ShareContent,
        template = view.template('templates/sharing.pt'))

    csrf = True
    fields = form.Fieldset(
        form.FieldFactory(
            'text',
            'term',
            title = u'Search term',
            description = 'Searches users by login and email',
            missing = u'',
            default = u''))

    users = None
    bsize = 15

    def form_content(self):
        return {'term': self.request.session.get('sharing-search-term', '')}

    def get_principal(self, id):
        return ptah.resolve(id)

    def update(self):
        super(SharingForm, self).update()

        request = self.request
        context = self.context

        self.roles = [r for r in ptah.get_roles().values() if not r.system]
        self.local_roles = local_roles = context.__local_roles__

        term = request.session.get('sharing-search-term', '')
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

        self.request.session['sharing-search-term'] = data['term']
        raise HTTPFound(location = self.request.url)
