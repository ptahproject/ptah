import transaction
import ptah, ptah_crowd
from memphis import config
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from base import Base


class TestModule(Base):

    def test_manage_module(self):
        from ptah.manage import PtahManageRoute
        from ptah_crowd.module import CrowdModule

        request = DummyRequest()

        ptah.authService.set_userid('test')
        ptah.PTAH_CONFIG['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['crowd']

        self.assertIsInstance(mod, CrowdModule)

    def test_manage_module_get(self):
        from ptah_crowd.module import CrowdModule, UserWrapper
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        uri = user.uri
        Session.add(user)
        Session.flush()

        mod = CrowdModule(None, DummyRequest())

        self.assertRaises(KeyError, mod.__getitem__, 'unkown')

        wu = mod[str(user.pid)]

        self.assertIsInstance(wu, UserWrapper)
        self.assertEqual(wu.user.uri, uri)
