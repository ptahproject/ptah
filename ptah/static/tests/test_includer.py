from pyramid.response import Response
from base import BaseTestCase


class TestIncluder(BaseTestCase):

    def test_components(self):

        def view(request):
            request.include('anycomponent')
            return Response('<html><head></head><body></body></html>')

        self.config.add_route('view', '/')
        self.config.add_view(view, route_name='view')
        self.config.add_bower_components(
            'ptah.static:tests/bower_components')

        app = self.make_app()
        response = app.get('/')

        self.assertEqual(response.body, (
            b'<html><head>'
            b'<script type="text/javascript" '
            b'src="/bowerstatic/components/'
            b'anycomponent/1.0.0/anycomponent.js">'
            b'</script></head><body></body></html>'))

        response = app.get('/bowerstatic/components/'
                           'anycomponent/1.0.0/anycomponent.js')

        self.assertEqual(response.body, b'/* anycomponent.js */\n')

    def test_custom_components(self):

        def view(request):
            request.include('anycomponent', 'lib')
            return Response('<html><head></head><body></body></html>')

        self.config.add_route('view', '/')
        self.config.add_view(view, route_name='view')
        self.config.add_bower_components(
            'ptah.static:tests/bower_components', name='lib')

        app = self.make_app()
        response = app.get('/')

        self.assertEqual(response.body, (
            b'<html><head>'
            b'<script type="text/javascript" '
            b'src="/bowerstatic/lib/'
            b'anycomponent/1.0.0/anycomponent.js">'
            b'</script>'
            b'</head><body></body></html>'))

        response = app.get('/bowerstatic/lib/'
                           'anycomponent/1.0.0/anycomponent.js')

        self.assertEqual(response.body, b'/* anycomponent.js */\n')

    def test_components_in_template(self):

        def view(request):
            return {}

        self.config.include('pyramid_chameleon')
        self.config.add_route('view', '/')
        self.config.add_view(
            view, route_name='view',
            renderer='ptah.static:tests/templates/index.pt')
        self.config.add_bower_components(
            'ptah.static:tests/bower_components')

        app = self.make_app()
        response = app.get('/')

        self.assertIn(
            b'<script type="text/javascript" '
            b'src="/bowerstatic/components/'
            b'anycomponent/1.0.0/anycomponent.js">'
            b'</script>', response.body)

        response = app.get('/bowerstatic/components/'
                           'anycomponent/1.0.0/anycomponent.js')

        self.assertEqual(response.body, b'/* anycomponent.js */\n')

    def test_components_not_exist_errors(self):
        from ptah.static import Error

        self.assertRaises(Error, self.request.include, 'anycomponent')
        self.assertRaises(Error, self.request.include, 'not-exist-component')

    def test_local_component(self):

        def view(request):
            request.include('myapp')
            return Response('<html><head></head><body></body></html>')

        self.config.add_route('view', '/')
        self.config.add_view(view, route_name='view')
        self.config.add_bower_components(
            'ptah.static:tests/bower_components')
        self.config.add_bower_component(
            'ptah.static:tests/local_component', '1.0.0')

        app = self.make_app()
        response = app.get('/')

        self.assertEqual(response.body, (
            b'<html><head>'
            b'<script type="text/javascript" src='
            b'"/bowerstatic/components/anycomponent/1.0.0/anycomponent.js">'
            b'</script>\n<script type="text/javascript" '
            b'src="/bowerstatic/components/myapp/1.0.0/myapp.js"></script>'
            b'</head><body></body></html>'))

        response = app.get('/bowerstatic/components/myapp/1.0.0/myapp.js')

        self.assertEqual(response.body, b'/* myapp.js */\n')

    def test_local_component_in_template(self):

        def view(request):
            return {}

        self.config.include('pyramid_chameleon')
        self.config.add_route('view', '/')
        self.config.add_view(
            view, route_name='view',
            renderer='ptah.static:tests/templates/index_local.pt')
        self.config.add_bower_components(
            'ptah.static:tests/bower_components')
        self.config.add_bower_component(
            'ptah.static:tests/local_component', '1.0.0')

        app = self.make_app()
        response = app.get('/')

        self.assertIn((
            b'<script type="text/javascript" src='
            b'"/bowerstatic/components/anycomponent/1.0.0/anycomponent.js">'
            b'</script>\n<script type="text/javascript" '
            b'src="/bowerstatic/components/myapp/1.0.0/myapp.js"></script>'),
            response.body)

        response = app.get('/bowerstatic/components/'
                           'anycomponent/1.0.0/anycomponent.js')

        self.assertEqual(response.body, b'/* anycomponent.js */\n')

        response = app.get('/bowerstatic/components/myapp/1.0.0/myapp.js')

        self.assertEqual(response.body, b'/* myapp.js */\n')

    def test_custom_local_component(self):

        def view(request):
            request.include('myapp', 'lib')
            return Response('<html><head></head><body></body></html>')

        self.config.add_route('view', '/')
        self.config.add_view(view, route_name='view')
        self.config.add_bower_components(
            'ptah.static:tests/bower_components', name='lib')
        self.config.add_bower_component(
            'ptah.static:tests/local_component', '1.0.0', name='lib')

        app = self.make_app()
        response = app.get('/')

        self.assertEqual(response.body, (
            b'<html><head>'
            b'<script type="text/javascript" src='
            b'"/bowerstatic/lib/anycomponent/1.0.0/anycomponent.js">'
            b'</script>\n<script type="text/javascript" '
            b'src="/bowerstatic/lib/myapp/1.0.0/myapp.js"></script>'
            b'</head><body></body></html>'))

        response = app.get('/bowerstatic/lib/myapp/1.0.0/myapp.js')

        self.assertEqual(response.body, b'/* myapp.js */\n')
