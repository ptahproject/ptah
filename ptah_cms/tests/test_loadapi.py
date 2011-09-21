import transaction
from memphis import config
from pyramid.httpexceptions import HTTPForbidden

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

    def test_loadapi_loadcontent(self):
        content = Content(title='Content')
        uuid = content.__uuid__

        ptah_cms.Session.add(content)
        transaction.commit()

        content = ptah_cms.loadContent(uuid)
        self.assertEqual(content.__uuid__, uuid)

    def test_loadapi_loadcontent_with_parents(self):
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

        content = ptah_cms.loadContent(c_uuid)
        self.assertEqual(content.__parent__.__uuid__, co_uuid)

    def test_loadapi_loadcontent_permission(self):
        from ptah_cms import content
        
        allow = False
        def checkPermission(content, permission, r=None, t=True):
            if not allow:
                return False

            return True

        # monkey patch
        content.checkPermission = checkPermission

        c = Content(title='Content')
        uuid = c.__uuid__
        ptah_cms.Session.add(c)
        transaction.commit()

        self.assertRaises(HTTPForbidden, ptah_cms.loadContent, uuid, 'View')

        allow = True
        c = ptah_cms.loadContent(uuid, 'View')
        self.assertEqual(c.__uuid__, uuid)

        # remove monkey patch
        content.checkPermission = ptah.checkPermission
