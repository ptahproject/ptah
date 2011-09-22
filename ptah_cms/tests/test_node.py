import uuid
import transaction
from memphis import config

from base import Base


class TestNode(Base):

    def test_node_instance(self):
        import ptah_cms
        
        # it not possible to instatiate Node
        self.assertRaises(ptah_cms.Node)

    def test_node(self):
        import ptah_cms
        
        class MyContent(ptah_cms.Node):
            
            def __uuid_generator__(self):
                return uuid.uuid4().get_hex()

        content = MyContent()
        _uuid = content.__uuid__
        ptah_cms.Session.add(content)
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uuid__ == _uuid).one()

        self.assertTrue(isinstance(c, ptah_cms.Node))
        
    def test_polymorphic_node(self):
        import ptah_cms

        class MyContent(ptah_cms.Node):

            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            
            def __uuid_generator__(self):
                return uuid.uuid4().get_hex()

        content = MyContent()
        _uuid = content.__uuid__
        ptah_cms.Session.add(content)
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uuid__ == _uuid).one()

        self.assertTrue(isinstance(c, MyContent))

    def test_node_parent(self):
        import ptah_cms

        class MyContent(ptah_cms.Node):

            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            
            def __uuid_generator__(self):
                return uuid.uuid4().get_hex()

        parent = MyContent()
        parent_uuid = parent.__uuid__

        content = MyContent(__parent__ = parent)
        __uuid = content.__uuid__

        ptah_cms.Session.add(parent)
        ptah_cms.Session.add(content)
        transaction.commit()
                
        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uuid__ == __uuid).one()

        self.assertTrue(c.__parent_id__ == parent_uuid)
        self.assertTrue(c.__parent_ref__.__uuid__ == parent_uuid)

    def test_node_local_roles(self):
        import ptah, ptah_cms

        class MyContent(ptah_cms.Node):

            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            
            def __uuid_generator__(self):
                return uuid.uuid4().get_hex()

        content = MyContent()
        __uuid = content.__uuid__

        self.assertTrue(ptah.ILocalRolesAware.providedBy(content))

        ptah_cms.Session.add(content)
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uuid__ == __uuid).one()

        c.__local_roles__['userid'] = ('role:1',)
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uuid__ == __uuid).one()
        self.assertTrue(c.__local_roles__ == {u'userid': [u'role:1']})

    def test_node_owners(self):
        import ptah, ptah_cms

        class MyContent(ptah_cms.Node):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            def __uuid_generator__(self):
                return uuid.uuid4().get_hex()

        content = MyContent()
        __uuid = content.__uuid__

        self.assertTrue(ptah.IOwnersAware.providedBy(content))

        ptah_cms.Session.add(content)
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uuid__ == __uuid).one()

        c.__owner__ = 'userid'
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uuid__ == __uuid).one()
        self.assertTrue(c.__owner__ == u'userid')

    def test_node_permissions(self):
        import ptah, ptah_cms

        class MyContent(ptah_cms.Node):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            def __uuid_generator__(self):
                return uuid.uuid4().get_hex()

        content = MyContent()
        __uuid = content.__uuid__

        self.assertTrue(ptah.IACLsAware.providedBy(content))

        ptah_cms.Session.add(content)
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uuid__ == __uuid).one()

        c.__acls__.append('map1')
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uuid__ == __uuid).one()
        self.assertTrue(c.__acls__ == [u'map1'])
