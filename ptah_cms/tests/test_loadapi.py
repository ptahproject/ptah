import transaction
from memphis import config
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden

import ptah
import ptah_cms
from ptah_cms import content

from base import Base


class Content(ptah_cms.Content):

    __type__ = ptah_cms.Type('content', 'Test Content')
    __uri_generator__ = ptah.UriGenerator('cms+content')


class Container(ptah_cms.Container):

    __type__ = ptah_cms.Type('container', 'Test Container')
    __uri_generator__ = ptah.UriGenerator('cms+container')


class TestLoadApi(Base):
    """ fixme: redesign tests to use custom resolver """

    def test_loadapi_loadnode(self):
        content = Content(title='Content')
        uri = content.__uri__

        ptah_cms.Session.add(content)
        transaction.commit()

        content = ptah_cms.loadNode(uri)
        self.assertEqual(content.__uri__, uri)

    def test_loadapi_loadnode_notfound(self):
        self.assertRaises(HTTPNotFound, ptah_cms.loadNode, 'unknown')

    def test_loadapi_loadnode_with_parents(self):
        content = Content(title='Content')
        container = Container(__name__='container', __path__='/container/')

        c_uri = content.__uri__
        co_uri = container.__uri__
        ptah_cms.Session.add(container)
        ptah_cms.Session.add(content)
        transaction.commit()

        container = ptah.resolve(co_uri)
        container['content'] = ptah.resolve(c_uri)
        transaction.commit()

        content = ptah_cms.loadNode(c_uri)
        self.assertEqual(content.__parent__.__uri__, co_uri)

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
        uri = c.__uri__
        ptah_cms.Session.add(c)
        transaction.commit()

        self.assertRaises(HTTPForbidden, ptah_cms.loadNode, uri, 'View')

        allow = True
        c = ptah_cms.loadNode(uri, 'View')
        self.assertEqual(c.__uri__, uri)

        # remove monkey patch
        ptah.checkPermission = orig_checkPermission
