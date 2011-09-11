import colander
from webob.exc import HTTPFound
from memphis import config, view, form

import ptah
from interfaces import _, ILocalRolesAware


class SearchSchema(colander.Schema):
    """ search users """

    term = colander.SchemaNode(
        colander.Str(),
        title = _(u'Search term'),
        description = _('Ptah searches users by login and email'),
        missing = u'',
        default = u'')


class SharingForm(form.Form):
    view.pyramidView(
        'sharing.html', ILocalRolesAware, layout='',
        template = view.template('ptah.security:templates/sharing.pt'))

    csrf = True
    fields = form.Fields(SearchSchema)

    users = None
    bsize = 15

    def getContent(self):
        return {'term': self.request.session.get('sharing-term', '')}

    def getPrincipal(self, id):
        return ptah.security.authService.getPrincipal(id)

    def update(self):
        super(SharingForm, self).update()

        request = self.request
        context = self.context

        self.roles = [r for r in ptah.Roles.values() if not r.system]
        self.local_roles = local_roles = context.__local_roles__

        term = request.session.get('sharing-term', '')
        if term:
            self.users = list(ptah.security.authService.search(term))

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
        data, error = self.extractData()

        if not data['term']:
            self.message('Please specify search term', 'warning')
            return

        self.request.session['sharing-term'] = data['term']
        raise HTTPFound(location = self.request.url)
