""" introspect module """
import ptah
import colander
import sqlalchemy as sqla
from zope import interface
from pyramid.httpexceptions import HTTPFound
from memphis import view, form, config

from provider import Session
from provider import CrowdUser as SQLUser
from memberprops import MemberProperties

from interfaces import _


class ICrowdModule(ptah.IPtahModule):
    """ marker interface for crowd module """


class ICrowdUser(interface.Interface):
    """ wrapper for actual user """

    user = interface.Attribute('Wrapped user object')


class CrowdModule(ptah.PtahModule):
    """ Basic user management module. """

    config.utility(name='crowd')
    interface.implementsOnly(ICrowdModule)

    name = 'crowd'
    title = 'Crowd'

    def __getitem__(self, key):
        if key:
            user = SQLUser.getById(key)
            if user is not None:
                return CrowdUser(user, self)

        raise KeyError(key)


class CrowdUser(object):
    interface.implements(ICrowdUser)

    def __init__(self, user, parent):
        self.user = user
        self.__name__ = str(user.pid)
        self.__parent__ = parent


view.registerPagelet(
    'ptah-module-actions', ICrowdModule,
    template = view.template('ptah.crowd:templates/ptah-actions.pt'))


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
        'search.html', ICrowdModule, 'ptah-manage', default=True,
        template = view.template('ptah.crowd:templates/search.pt'))

    __doc__ = 'List/search users view'
    __intr_path__ = '/ptah-manage/crowd/search.html'

    csrf = True
    fields = form.Fields(SearchSchema)

    users = None
    page = ptah.BatchPage(15)

    def getContent(self):
        return {'term': self.request.session.get('ptah-search-term', '')}

    def update(self):
        super(SearchUsers, self).update()

        request = self.request
        uids = request.POST.getall('uid')

        if 'activate' in request.POST and uids:
            Session.query(MemberProperties)\
                .filter( MemberProperties.uuid.in_(uids))\
                .update({'suspended': False}, False)
            self.message("Selected accounts have been activated.", 'info')

        if 'suspend' in request.POST and uids:
            Session.query(MemberProperties).filter(
                MemberProperties.uuid.in_(uids))\
                .update({'suspended': True}, False)
            self.message("Selected accounts have been suspended.", 'info')

        if 'validate' in request.POST and uids:
            Session.query(MemberProperties).filter(
                MemberProperties.uuid.in_(uids))\
                .update({'validated': True}, False)
            self.message("Selected accounts have been validated.", 'info')

        term = request.session.get('ptah-search-term', '')
        if term:
            self.users = Session.query(SQLUser) \
                .filter(SQLUser.email.contains('%%%s%%'%term))\
                .order_by(sqla.sql.asc('name')).all()
        else:
            self.size = Session.query(SQLUser).count()

            try:
                current = int(request.params.get('batch', None))
                if not current:
                    current = request.session.get('crowd-current-batch')
                    if not current:
                        current = 1
                    else:
                        request.session['crowd-current-batch'] = current
            except:
                current = request.session.get('crowd-current-batch')
                if not current:
                    current = 1

            self.current = current

            self.pages, self.prev, self.next = self.page(self.size,self.current)

            offset, limit = self.page.offset(current)
            self.users = Session.query(SQLUser)\
                    .offset(offset).limit(limit).all()

    @form.button(_('Search'), actype=form.AC_PRIMARY)
    def search(self):
        data, error = self.extractData()

        if not data['term']:
            self.message('Please specify search term', 'warning')
            return

        self.request.session['ptah-search-term'] = data['term']
        raise HTTPFound(location = self.request.url)

    @form.button(_('Clear term'))
    def clear(self):
        if 'ptah-search-term' in self.request.session:
            del self.request.session['ptah-search-term']
