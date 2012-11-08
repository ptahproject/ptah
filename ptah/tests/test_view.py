# -*- coding: utf-8 -*-
import ptah
from ptah.testing import PtahTestCase


class Context(object):
    pass


class TestView(PtahTestCase):

    _init_ptah = False

    def test_view_app_root(self):
        view = ptah.View(Context(), self.request)
        self.assertEqual(view.application_url, 'http://example.com')

        view = ptah.View(Context(), self.request)
        self.request.application_url = 'http://example.com/'
        self.assertEqual(view.application_url, 'http://example.com')

    def test_view_update(self):
        view = ptah.View(Context(), self.request)
        self.assertEqual(view.update(), {})


class TestMasterLayout(PtahTestCase):

    def test_master_layout(self):
        from ptah.view import MasterLayout

        ml = MasterLayout(object(), self.request)
        self.assertIsNone(ml.user)
        self.assertEqual(ml.manage_url, 'http://example.com/ptah-manage')
        self.assertEqual(ml.actions, [])
