import os
from unittest import mock
import sys
import shutil
import tempfile
from pyramid.compat import NativeIO
from ptah.renderer import script as layer
from ptah.renderer.layer import ID_LAYER

from ptah.testing import BaseTestCase


class TestPlayerCommand(BaseTestCase):

    _includes = ['ptah.renderer']

    def setUp(self):
        super(TestPlayerCommand, self).setUp()

        self.dir = tempfile.mkdtemp()
        self.stdout = sys.stdout
        sys.stdout = self.out = NativeIO()

    def tearDown(self):
        shutil.rmtree(self.dir)
        sys.stdout = self.stdout
        super(TestPlayerCommand, self).tearDown()

    @mock.patch('ptah.renderer.script.bootstrap')
    def test_no_params(self, m_bs):
        m_bs.return_value = {'registry': self.registry}

        sys.argv[:] = ['ptah.renderer', 'ptah.renderer.ini']

        layer.main()

        val = self.out.getvalue()
        self.assertIn('[-l [LAYERS [LAYERS ...]]]', val)
        self.assertIn('[-lt [TEMPLATES [TEMPLATES ...]]]', val)

    @mock.patch('ptah.renderer.script.bootstrap')
    def test_list_categories_no_layers(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.registry[ID_LAYER] = {}

        sys.argv[:] = ['ptah.renderer', 'ptah.renderer.ini', '-l']

        layer.main()

        val = self.out.getvalue()
        self.assertIn('No layers are found.', val)

    @mock.patch('ptah.renderer.script.bootstrap')
    def test_list_categories(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.config.add_layer(
            'test1', path='ptah.renderer:tests/dir1/')
        self.config.add_layer(
            'test2', path='ptah.renderer:tests/bundle/')

        sys.argv[:] = ['ptah.renderer', 'ptah.renderer.ini', '-l']

        layer.main()

        val = self.out.getvalue()
        self.assertIn('* Layer: test1', val)
        self.assertIn('* Layer: test2', val)

    @mock.patch('ptah.renderer.script.bootstrap')
    def test_list_categories_limit(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.config.add_layer(
            'test1', path='ptah.renderer:tests/dir1/')
        self.config.add_layer(
            'test2', path='ptah.renderer:tests/bundle/')

        sys.argv[:] = ['ptah.renderer', 'ptah.renderer.ini', '-l', 'test2']

        layer.main()

        val = self.out.getvalue()
        self.assertNotIn('* Layer: test1', val)
        self.assertIn('* Layer: test2', val)

    @mock.patch('ptah.renderer.script.bootstrap')
    def test_list_templates(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.config.add_layer(
            'test1', path='ptah.renderer:tests/dir1/')
        self.config.add_layer(
            'test2', path='ptah.renderer:tests/bundle/')

        def test(): pass

        self.config.add_tmpl_filter(
            'test1:actions', test)

        sys.argv[:] = ['ptah.renderer', 'ptah.renderer.ini', '-lt']

        layer.main()

        val = self.out.getvalue()
        self.assertIn('* Layer: test1', val)
        self.assertIn('ptah.renderer:tests/dir1/', val)
        self.assertIn('actions: .pt (test_script.py: test)', val)
        self.assertIn('* Layer: test2', val)

    @mock.patch('ptah.renderer.script.bootstrap')
    def test_list_templates_limit(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.config.add_layer(
            'test1', path='ptah.renderer:tests/dir1/')
        self.config.add_layer(
            'test2', path='ptah.renderer:tests/bundle/')

        sys.argv[:] = ['ptah.renderer', 'ptah.renderer.ini', '-lt', 'test1']

        layer.main()

        val = self.out.getvalue()
        self.assertIn('* Layer: test1', val)
        self.assertIn('ptah.renderer:tests/dir1/', val)
        self.assertIn('actions: .pt', val)
        self.assertNotIn('* Layer: test2', val)

    @mock.patch('ptah.renderer.script.bootstrap')
    def test_list_templates_no_layers(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.registry[ID_LAYER] = {}

        sys.argv[:] = ['ptah.renderer', 'ptah.renderer.ini', '-lt']

        layer.main()

        val = self.out.getvalue()
        self.assertIn('No layers are found.', val)

    @mock.patch('ptah.renderer.script.bootstrap')
    def test_customize_template_fmt_bad(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.registry[ID_LAYER] = {}

        sys.argv[:] = ['ptah.renderer', 'ptah.renderer.ini', '-c', 'test', './']

        layer.main()

        val = self.out.getvalue()
        self.assertIn('Template format is wrong.', val)

    @mock.patch('ptah.renderer.script.bootstrap')
    def test_customize_template_no_layers(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.registry[ID_LAYER] = {}
        sys.argv[:] = ['ptah.renderer', 'ptah.renderer.ini', '-c', 'test:template.lt', './']

        layer.main()

        val = self.out.getvalue()
        self.assertIn('Layer "test" could not be found.', val)

    @mock.patch('ptah.renderer.script.bootstrap')
    def test_customize_template_no_template(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.config.add_layer(
            'test', path='ptah.renderer:tests/dir1/')

        sys.argv[:] = ['ptah.renderer', 'ptah.renderer.ini', '-c', 'test:template.lt', './']

        layer.main()

        val = self.out.getvalue()
        self.assertIn('Template "test:template.lt" could not be found.', val)

    @mock.patch('ptah.renderer.script.bootstrap')
    def test_customize_template_no_dest(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.config.add_layer(
            'test', path='ptah.renderer:tests/dir1/')

        sys.argv[:] = ['ptah.renderer', 'ptah.renderer.ini', '-c',
                       'test:view.lt', './blah-blah-blah']

        layer.main()

        val = self.out.getvalue()
        self.assertIn('Destination directory is not found.', val)

    @mock.patch('ptah.renderer.script.bootstrap')
    def test_customize_success(self, m_bs):
        m_bs.return_value = {'registry': self.registry}
        self.config.add_layer(
            'test', path='ptah.renderer:tests/dir1/')

        sys.argv[:] = ['ptah.renderer', 'ptah.renderer.ini', '-c', 'test:view.lt', self.dir]

        layer.main()

        self.assertTrue(os.path.join(self.dir, 'view.pt'))
