import transaction
import ptah, ptah_crowd
from memphis import form
from pyramid.testing import DummyRequest

from base import Base


class TestCheckLogin(Base):

    def test_check_login(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        Session.add(user)
        transaction.commit()

        request = DummyRequest()

        self.assertRaises(
            form.Invalid, ptah_crowd.checkLoginValidator, None, 'login')
        
        class Field(object):
            """ """

        field = Field()
        field.content = 'login'
        ptah_crowd.checkLoginValidator(field, 'login')

        field.content = 'other-login'
        self.assertRaises(
            form.Invalid, ptah_crowd.checkLoginValidator, field, 'login')

    def test_lower(self):
        from ptah_crowd.schemas import lower
        
        self.assertEqual(lower('Tttt'), 'tttt')
        self.assertEqual(lower('tttT'), 'tttt')
        self.assertEqual(lower(lower), lower)
    
