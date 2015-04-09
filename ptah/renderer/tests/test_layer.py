import mock
from pyramid.exceptions import ConfigurationError
from pyramid.exceptions import ConfigurationConflictError

from ptah.testing import BaseTestCase


class TestLayerDirective(BaseTestCase):

    def test_layer_directive(self):
        self.assertFalse(hasattr(self.config, 'add_layer'))
        self.assertFalse(hasattr(self.config, 'add_layers'))
        self.assertFalse(hasattr(self.config, 'add_tmpl_filter'))
        self.config.include('ptah.renderer')

        self.assertTrue(hasattr(self.config, 'add_layer'))
        self.assertTrue(hasattr(self.config, 'add_layers'))
        self.assertTrue(hasattr(self.config, 'add_tmpl_filter'))


class TestLayer(BaseTestCase):

    _includes = ['ptah.renderer']
    _auto_commit = False

    def test_layer_registration(self):
        from ptah.renderer.layer import ID_LAYER

        self.config.add_layer(
            'test', path='ptah.renderer:tests/dir1/')
        self.config.commit()

        data = self.registry.get(ID_LAYER)
        self.assertIn('test', data)
        self.assertEqual(len(data['test']), 1)
        self.assertEqual(data['test'][0]['name'], '')
        self.assertTrue(data['test'][0]['path'].endswith(
            'ptah/renderer/tests/dir1/'))

    def test_layer_path_required(self):
        self.assertRaises(
            ConfigurationError, self.config.add_layer, 'test')

    def test_multple_layer_registration(self):
        from ptah.renderer.layer import ID_LAYER

        self.config.add_layer(
            'test', path='ptah.renderer:tests/dir1/')
        self.config.commit()

        self.config.add_layer(
            'test', 'custom', path='ptah.renderer:tests/bundle/dir1/')
        self.config.commit()

        data = self.registry.get(ID_LAYER)
        self.assertIn('test', data)
        self.assertEqual(len(data['test']), 2)
        self.assertEqual(data['test'][0]['name'], 'custom')
        self.assertTrue(data['test'][0]['path'].endswith(
            'ptah/renderer/tests/bundle/dir1/'))
        self.assertEqual(data['test'][1]['name'], '')
        self.assertTrue(data['test'][1]['path'].endswith(
            'ptah/renderer/tests/dir1/'))

    def test_register_layers(self):
        from ptah.renderer.layer import ID_LAYER

        self.config.add_layers(
            'custom', path='ptah.renderer:tests/bundle/')
        self.config.commit()

        data = self.registry.get(ID_LAYER)
        self.assertIn('dir1', data)
        self.assertEqual(len(data['dir1']), 1)
        self.assertEqual(data['dir1'][0]['name'], 'custom')
        self.assertTrue(data['dir1'][0]['path'].endswith(
            'ptah/renderer/tests/bundle/dir1'))

    def test_reg_conflict(self):
        self.config.commit()

        self.config.add_layer(
            'test', path='ptah.renderer:tests/dir1/')
        self.config.add_layer(
            'test', path='ptah.renderer:tests/bundle/dir1/')

        self.assertRaises(
            ConfigurationConflictError, self.config.commit)


class TestTmplFilter(BaseTestCase):

    _includes = ['ptah.renderer']

    def test_add_tmpl_filter_err(self):
        def _filter(context, request):
            return {}

        self.assertRaises(
            ConfigurationError,
            self.config.add_tmpl_filter, 'test:view', _filter)

    @mock.patch('ptah.renderer.layer.venusian')
    def test_add_tmpl_filter_deco_err(self, m_venusian):
        import ptah.renderer

        @ptah.renderer.tmpl_filter('test:view')
        def _filter(context, request):
            return {}

        wrp, cb = m_venusian.attach.call_args[0]

        self.assertIs(wrp, _filter)

        m_venusian.config.with_package.return_value = self.config
        self.assertRaises(
            ConfigurationError, cb, m_venusian, 't', _filter)

    def test_add_tmpl_filter(self):
        from ptah.renderer.layer import ID_LAYER

        self.config.add_layer(
            'test', path='ptah.renderer:tests/dir1/')
        self.config.add_layer(
            'test', 'custom', path='ptah.renderer:tests/bundle/dir1/')

        def _filter(context, request):
            return {}

        self.config.add_tmpl_filter('test:view', _filter)

        data = self.registry.get(ID_LAYER)
        self.assertIn('test', data)
        self.assertEqual(len(data['test']), 2)
        self.assertEqual(data['test'][1]['name'], '')
        self.assertIs(_filter, data['test'][1]['filters']['view'])
