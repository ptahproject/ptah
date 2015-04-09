from base import BaseTestCase


class TestLocalComponents(BaseTestCase):

    def test_add(self):

        self.config.add_bower_components(
            'ptah.static:tests/bower_components')
        self.config.add_bower_component(
            'ptah.static:tests/local_component')

        bower = self.request.get_bower()

        collection = bower._component_collections['components']

        self.assertIn('myapp', collection._components)

    def test_add_custom(self):

        self.config.add_bower_components(
            'ptah.static:tests/bower_components', name='lib')
        self.config.add_bower_component(
            'ptah.static:tests/local_component', name='lib')

        bower = self.request.get_bower()

        self.assertIn('lib', bower._component_collections)

        collection = bower._component_collections['lib']

        self.assertIn('myapp', collection._components)

    def test_add_error(self):
        from ptah.static import Error

        self.assertRaises(Error, self.config.add_bower_component,
                          'ptah.static:tests/local_component')
