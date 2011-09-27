import ptah
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
            __uri_generator__ = ptah.UriGenerator('test')

        content = MyContent()
        _uri = content.__uri__
        ptah_cms.Session.add(content)
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uri__ == _uri).one()

        self.assertTrue(isinstance(c, ptah_cms.Node))

    def test_polymorphic_node(self):
        import ptah_cms

        class MyContent(ptah_cms.Node):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_generator__ = ptah.UriGenerator('test')

        content = MyContent()
        _uri = content.__uri__
        ptah_cms.Session.add(content)
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uri__ == _uri).one()

        self.assertTrue(isinstance(c, MyContent))

    def test_node_parent(self):
        import ptah_cms

        class MyContent(ptah_cms.Node):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_generator__ = ptah.UriGenerator('test')

        parent = MyContent()
        parent_uri = parent.__uri__

        content = MyContent(__parent__ = parent)
        __uri = content.__uri__

        ptah_cms.Session.add(parent)
        ptah_cms.Session.add(content)
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uri__ == __uri).one()

        self.assertTrue(c.__parent_uri__ == parent_uri)
        self.assertTrue(c.__parent_ref__.__uri__ == parent_uri)

    def test_node_local_roles(self):
        import ptah, ptah_cms

        class MyContent(ptah_cms.Node):
            __uri_generator__ = ptah.UriGenerator('test')
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}

        content = MyContent()
        __uri = content.__uri__

        self.assertTrue(ptah.ILocalRolesAware.providedBy(content))

        ptah_cms.Session.add(content)
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uri__ == __uri).one()

        c.__local_roles__['userid'] = ('role:1',)
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uri__ == __uri).one()
        self.assertTrue(c.__local_roles__ == {u'userid': [u'role:1']})

    def test_node_owners(self):
        import ptah, ptah_cms

        class MyContent(ptah_cms.Node):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_generator__ = ptah.UriGenerator('test')

        content = MyContent()
        __uri = content.__uri__

        self.assertTrue(ptah.IOwnersAware.providedBy(content))

        ptah_cms.Session.add(content)
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uri__ == __uri).one()

        c.__owner__ = 'userid'
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uri__ == __uri).one()
        self.assertTrue(c.__owner__ == u'userid')

    def test_node_permissions(self):
        import ptah, ptah_cms

        class MyContent(ptah_cms.Node):
            __mapper_args__ = {'polymorphic_identity': 'mycontent'}
            __uri_generator__ = ptah.UriGenerator('test')

        content = MyContent()
        __uri = content.__uri__

        self.assertTrue(ptah.IACLsAware.providedBy(content))

        ptah_cms.Session.add(content)
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uri__ == __uri).one()

        c.__acls__.append('map1')
        transaction.commit()

        c = ptah_cms.Session.query(ptah_cms.Node).filter(
            ptah_cms.Node.__uri__ == __uri).one()
        self.assertTrue(c.__acls__ == [u'map1'])
