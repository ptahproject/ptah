import transaction
import ptah
from ptah import config
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound

from base import Base


TestRole = ptah.Role('test', 'Test role')

class Container(ptah.cms.Container):

    __type__ = ptah.cms.Type('container', 'Test Container')
    __uri_factory__ = ptah.UriFactory('cms-container')


class TestSharingForm(Base):

    def test_sharingform_search(self):
        from ptah.cmsapp.sharing import SharingForm

        container = Container()

        form = SharingForm(container, DummyRequest(
                POST={'form.buttons.search': 'Search',
                      'term': 'search term'}))
        form.csrf = False
        try:
            form.update()
        except Exception, res:
            pass

        self.assertIsInstance(res, HTTPFound)
        self.assertIn('sharing-search-term', form.request.session)
        self.assertEqual(
            form.request.session['sharing-search-term'], 'search term')

    def test_sharingform_search_error(self):
        from ptah.cmsapp.sharing import SharingForm

        container = Container()

        form = SharingForm(container, DummyRequest(
                POST={'form.buttons.search': 'Search'}))
        form.csrf = False
        form.update()

        self.assertIn('Please specify search term', 
                      form.request.session['msgservice'][0])

    def test_sharingform_update(self):
        from ptah.cmsapp.sharing import SharingForm
        from ptah.crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        Session.add(user)
        Session.flush()

        container = Container()

        form = SharingForm(container, DummyRequest(
                session={'sharing-search-term': 'email'}))
        form.csrf = False
        form.update()

        self.assertEqual(len(form.users), 1)
        self.assertEqual(form.users[0].uri, user.uri)
        self.assertIs(form.local_roles, container.__local_roles__)
        self.assertEqual(len(form.roles), 1)
        self.assertIs(form.roles[0], TestRole)
        self.assertEqual(form.get_principal(user.uri).uri, user.uri)

    def test_sharingform_save(self):
        from ptah.cmsapp.sharing import SharingForm
        from ptah.crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        Session.add(user)
        Session.flush()

        container = Container()

        form = SharingForm(container, DummyRequest(
                session={'sharing-search-term': 'email'},
                POST={'form.buttons.save': 'Save',
                      'userid-%s'%user.uri: 'on',
                      'user-%s-role:test'%user.uri: 'on'}))
        form.csrf = False
        form.update()

        self.assertIn(user.uri, container.__local_roles__)
        self.assertIn(TestRole.id, container.__local_roles__[user.uri])

    def test_sharingform_unset(self):
        from ptah.cmsapp.sharing import SharingForm
        from ptah.crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        Session.add(user)
        Session.flush()

        container = Container()
        container.__local_roles__ = {user.uri: [TestRole.id]}

        form = SharingForm(container, DummyRequest(
                session={'sharing-search-term': 'email'},
                POST={'form.buttons.save': 'Save',
                      'userid-%s'%user.uri: 'on'}))
        form.csrf = False
        form.update()

        self.assertNotIn(user.uri, container.__local_roles__)
