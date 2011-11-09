import unittest


class TestViewLayersManager(unittest.TestCase):

    def test_register(self):
        from ptah.view.customize import _ViewLayersManager

        manager = _ViewLayersManager()

        manager.register('test', (1,))
        manager.register('test2', (1,))
        manager.register('', (1,))

        self.assertEqual(manager.layers[(1,)], ['', 'test', 'test2'])

    def test_enabled(self):
        from ptah.view.customize import _ViewLayersManager

        manager = _ViewLayersManager()

        manager.register('test', (1,))
        manager.register('test2', (1,))
        manager.register('', (1,))

        self.assertFalse(manager.enabled('test', (1,)))
        self.assertTrue(manager.enabled('test2', (1,)))
        self.assertFalse(manager.enabled('test', (2,)))
