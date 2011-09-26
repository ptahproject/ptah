import transaction
from memphis import config
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden

import ptah
import ptah_cms
from ptah_cms import content

from base import Base


class Content(ptah_cms.Content):

    __type__ = ptah_cms.Type('content', 'Test Content')
    __uuid_generator__ = ptah.UUIDGenerator('cms+content')


class Container(ptah_cms.Container):

    __type__ = ptah_cms.Type('container', 'Test Container')
    __uuid_generator__ = ptah.UUIDGenerator('cms+container')


class TestLoadApi(Base):
    """ fixme: redesign tests to use custom resolver """

    def test_loadapi_loadnode(self):
        content = Content(title='Content')
        uuid = content.__uuid__

        ptah_cms.Session.add(content)
        transaction.commit()

        content = ptah_cms.loadNode(uuid)
        self.assertEqual(content.__uuid__, uuid)

    def test_loadapi_loadnode_notfound(self):
        self.assertRaises(HTTPNotFound, ptah_cms.loadNode, 'unknown')

    def test_loadapi_loadnode_with_parents(self):
        content = Content(title='Content')
        container = Container(__name__='container', __path__='/container/')

        c_uuid = content.__uuid__
        co_uuid = container.__uuid__
        ptah_cms.Session.add(container)
        ptah_cms.Session.add(content)
        transaction.commit()

        container = ptah.resolve(co_uuid)
        container['content'] = ptah.resolve(c_uuid)
        transaction.commit()

        content = ptah_cms.loadNode(c_uuid)
        self.assertEqual(content.__parent__.__uuid__, co_uuid)

    def test_loadapi_loadnode_permission(self):
        import ptah

        allow = False
        def checkPermission(permission, content, r=None, t=True):
            if not allow:
                return False

            return True

        # monkey patch
        orig_checkPermission = ptah.checkPermission
        ptah.checkPermission = checkPermission

        c = Content(title='Content')
        uuid = c.__uuid__
        ptah_cms.Session.add(c)
        transaction.commit()

        self.assertRaises(HTTPForbidden, ptah_cms.loadNode, uuid, 'View')

        allow = True
        c = ptah_cms.loadNode(uuid, 'View')
        self.assertEqual(c.__uuid__, uuid)

        # remove monkey patch
        ptah.checkPermission = orig_checkPermission
