import ptah
from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest
from pyramid.view import render_view_to_response
from pyramid.httpexceptions import HTTPFound


class TestSettingsModule(PtahTestCase):

    def test_settings_module(self):
        from ptah.manage.manage import PtahManageRoute
        from ptah.manage.settings import SettingsModule

        request = DummyRequest()

        ptah.auth_service.set_userid('test')
        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['settings']

        self.assertIsInstance(mod, SettingsModule)

    def test_settings_view(self):
        from ptah.manage.settings import SettingsModule, SettingsView

        request = DummyRequest()

        mod = SettingsModule(None, request)

        res = render_view_to_response(mod, request, '', False)
        self.assertEqual(res.status, '200 OK')


class TestSettingsTTW(PtahTestCase):

    _init_ptah = False

    def test_traverse_ttw(self):
        from ptah.manage.settings import SettingsModule, SettingsWrapper

        ptah.register_settings(
            'test',
            ptah.form.TextField('node1', default='test1'),
            ptah.form.TextField('node2', default='test2', tint=True),
            title = 'Test settings')

        self.init_ptah()

        grp = ptah.get_settings('test', self.registry)
        mod = SettingsModule(None, self.request)

        self.assertRaises(
            KeyError,
            mod.__getitem__, 'test')

        grp.__ttw__ = True

        tgrp = mod['test']
        self.assertIs(tgrp.group, grp)
        self.assertIsInstance(tgrp, SettingsWrapper)

    def test_edit_form(self):
        from ptah.manage.settings import SettingsModule, EditForm

        ptah.register_settings(
            'test',
            ptah.form.TextField('node1', default='test1'),
            ptah.form.TextField('node2', default='test2'),
            title = 'Test settings',
            ttw = True,
            ttw_skip_fields = ('node2',))

        self.init_ptah()

        mod = SettingsModule(None, self.request)
        grp = mod['test']
        settings = grp.group

        form = EditForm(grp, self.request)

        self.assertEqual(form.label, settings.__title__)
        self.assertEqual(form.description, settings.__description__)
        self.assertIs(form.form_content(), settings)

        fields = form.fields
        self.assertIn('node1', fields)
        self.assertNotIn('node2', fields)

        res = form.back_handler()
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '..')

        form.update()
        form.modify_handler()
        self.assertIn('Settings have been modified.',
                      ptah.render_messages(self.request))
