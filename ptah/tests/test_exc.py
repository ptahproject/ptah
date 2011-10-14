import ptah
from memphis import config, view
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden

from base import Base


class TestExceptions(Base):

    def test_not_found(self):
        from ptah.exc import NotFound

        class Context(object):
            """ """

        request = DummyRequest()
        request.root = Context()

        excview = NotFound(HTTPNotFound(), request)
        excview.update()

        self.assertIs(excview.__parent__, request.root)
        self.assertEqual(request.response.status, '404 Not Found')
