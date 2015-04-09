from ptah.renderer.layer import ID_LAYER

from ptah.testing import BaseTestCase


class TestOrder(BaseTestCase):

    _includes = ['ptah.renderer']
    _auto_commit = False
    _settings = {'layer.order.test': 'l1 l2 l3'}

    def test_custom_dir(self):
        self.config.add_layer(
            'test', 'l1', path='ptah.renderer:tests/dir1/')
        self.config.add_layer(
            'test', 'l2', path='ptah.renderer:tests/bundle/dir1/')
        self.config.commit()

        storage = self.registry.get(ID_LAYER)
        self.assertIn('test', storage)
        self.assertEqual(2, len(storage['test']))
        self.assertEqual('l1', storage['test'][0]['name'])
        self.assertEqual('l2', storage['test'][1]['name'])


class TestOrderUnknown(BaseTestCase):

    _includes = ['ptah.renderer']
    _auto_commit = False
    _settings = {'layer.order.test2': 'l1 l2 l3'}

    def test_custom_dir(self):
        self.config.add_layer(
            'test', 'l1', path='ptah.renderer:tests/dir1/')
        self.config.add_layer(
            'test', 'l2', path='ptah.renderer:tests/bundle/dir1/')
        self.config.commit()

        storage = self.registry.get(ID_LAYER)
        self.assertIn('test', storage)
        self.assertNotIn('test2', storage)
