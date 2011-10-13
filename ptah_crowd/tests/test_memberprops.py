import datetime
import transaction
import ptah, ptah_crowd

from base import Base


class TestMemberprops(Base):

    def test_memberprops_get(self):
        from ptah_crowd.memberprops import Session, MemberProperties

        props = ptah_crowd.get_properties('uid1')
        
        self.assertIsInstance(props, MemberProperties)
        self.assertEqual(props.uri, 'uid1')
        self.assertEqual(props.validated, False)
        self.assertEqual(props.suspended, False)
        self.assertIsInstance(props.joined, datetime.datetime)

        props = ptah_crowd.get_properties('uid1')
        self.assertEqual(props.uri, 'uid1')

        self.assertEqual(
            Session.query(MemberProperties).count(), 1)

    def test_memberprops_query(self):
        from ptah_crowd.memberprops import Session, MemberProperties

        props = ptah_crowd.query_properties('uid1')
        self.assertIsNone(props)
        self.assertEqual(
            Session.query(MemberProperties).count(), 0)
