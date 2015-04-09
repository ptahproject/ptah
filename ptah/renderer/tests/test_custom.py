from pyramid.exceptions import ConfigurationError
from ptah.renderer.layer import ID_LAYER

from ptah.testing import BaseTestCase


class TestSettingsError(BaseTestCase):

    _settings = {'layer.custom': 'unknown'}

    def test_custom(self):
        self.assertRaises(
            ConfigurationError, self.config.include, 'ptah.renderer')


class TestSettingsCustom(BaseTestCase):

    _includes = ['ptah.renderer']
    _auto_commit = False
    _settings = {'layer.custom': 'ptah.renderer:tests/bundle/'}

    def test_custom_dir(self):
        self.config.add_layer(
            'dir1', path='ptah.renderer:tests/dir1/')
        self.config.commit()

        storage = self.registry.get(ID_LAYER)
        self.assertIn('dir1', storage)
        self.assertEqual(2, len(storage['dir1']))
        self.assertEqual('layer_custom', storage['dir1'][0]['name'])
        self.assertEqual('', storage['dir1'][1]['name'])
