import colander
from zope import interface
from memphis import config, view, form
from pyramid.httpexceptions import HTTPFound

import ptah
import ptah_cms
from ptah import security


class SearchSchema(colander.Schema):
    """ search users """

    term = colander.SchemaNode(
        colander.Str(),
        title = u'Search term',
        description = 'Searches users by login and email',
        missing = u'',
        default = u'')


class SharingForm(form.Form):
    view.pyramidView(
        'sharing.html', security.ILocalRolesAware,
        template = view.template('ptah_app:templates/sharing.pt'))

    csrf = True
    fields = form.Fields(SearchSchema)

    users = None
    bsize = 15

    def getContent(self):
        return {'term': self.request.session.get('sharing-term', '')}

    def getPrincipal(self, id):
        return ptah.resolve(id)

    def update(self):
        super(SharingForm, self).update()

        request = self.request
        context = self.context

        self.roles = [r for r in ptah.Roles.values() if not r.system]
        self.local_roles = local_roles = context.__local_roles__

        term = request.session.get('sharing-term', '')
        if term:
            self.users = list(security.searchPrincipals(term))

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


sharingAction = ptah_cms.Action(**{'id': 'sharing',
                                   'title': 'Sharing',
                                   'action': 'sharing.html',
                                   'permission': ptah.View})

@config.adapter(security.ILocalRolesAware, name='sharing')
@interface.implementer(ptah_cms.IAction)
def sharingActionAdapter(context):
    return sharingAction
