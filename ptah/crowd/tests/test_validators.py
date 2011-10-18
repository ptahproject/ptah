import transaction
import ptah, ptah.crowd
from ptah import form
from pyramid.testing import DummyRequest

from base import Base


class TestCheckLogin(Base):

    def test_check_login(self):
        from ptah.crowd import login
        from ptah.crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        Session.add(user)
        transaction.commit()

        request = DummyRequest()

        self.assertRaises(
            form.Invalid, ptah.crowd.checkLoginValidator, None, 'login')

        class Field(object):
            """ """

        field = Field()
        field.content = 'login'
        ptah.crowd.checkLoginValidator(field, 'login')

        field.content = 'other-login'
        self.assertRaises(
            form.Invalid, ptah.crowd.checkLoginValidator, field, 'login')

    def test_lower(self):
        from ptah.crowd.schemas import lower

        self.assertEqual(lower('Tttt'), 'tttt')
        self.assertEqual(lower('tttT'), 'tttt')
        self.assertEqual(lower(lower), lower)
