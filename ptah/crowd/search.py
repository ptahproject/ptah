""" user management """
import colander
from zope import interface
from webob.exc import HTTPFound
from memphis import view, form, config
from sqlalchemy.sql.expression import asc

from models import Session, User
from interfaces import _, ICrowdModule


class SearchSchema(colander.Schema):
    """ search users """

    term = colander.SchemaNode(
        colander.Str(),
        title = _(u'Search term'),
        description = _('Ptah searches users by login and email'),
        missing = u'',
        default = u'')


class SearchUsers(form.Form):
    view.pyramidView(
        'search.html',
        context = ICrowdModule,
        route = 'ptah-manage', default = True,
        template = view.template('ptah.crowd:templates/search.pt'))

    fields = form.Fields(SearchSchema)

    users = None

    def getContent(self):
        return {'term': self.request.session.get('ptah-search-term', '')}

    def update(self):
        super(SearchUsers, self).update()

        request = self.request

        try:
            uids = [int(uid) for uid in request.POST.getall('uid')]
        except:
            uids = []

        if 'activate' in request.POST and uids:
            Session.query(User).filter(
                User.id.in_(uids)).update({'suspended': False}, False)
            self.message("Selected accounts have been activated.", 'info')

        if 'suspend' in request.POST and uids:
            Session.query(User).filter(
                User.id.in_(uids)).update({'suspended': True}, False)
            self.message("Selected accounts have been suspended.", 'info')

        if 'validate' in request.POST and uids:
            Session.query(User).filter(
                User.id.in_(uids)).update({'validated': True}, False)
            self.message("Selected accounts have been validated.", 'info')

        term = self.request.session.get('ptah-search-term', '')
        if term:
            self.users = Session.query(User) \
                .filter(User.email.contains('%%%s%%'%term))\
                .order_by(asc('name')).all()

    @form.button(_('Search'), actype=form.AC_PRIMARY)
    def search(self):
        data, error = self.extractData()

        if not data['term']:
            self.message('Please specify search term', 'warning')
            return

        self.request.session['ptah-search-term'] = data['term']
        raise HTTPFound(location = self.request.url)
