from webob.multidict import MultiDict
from pyramid.compat import text_
from pyramid.view import render_view_to_response
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

import ptah.form
from ptah.testing import BaseTestCase, TestCase


class TestFormWidgets(TestCase):

    def test_ctor(self):
        from ptah.form import Form, FormWidgets, Fieldset

        request = DummyRequest()
        form = Form(object(), request)
        fields = Fieldset()
        widgets = FormWidgets(fields, form, request)
        self.assertEqual(widgets.form_fields, fields)
        self.assertEqual(widgets.form, form)
        self.assertEqual(widgets.request, request)

    def test_extract_convert_strings(self):
        from ptah.form import Invalid, Form, FormWidgets

        class MyForm(Form):
            def validate(self, data, errors):
                errors.extend((Invalid('error1'), 'error2'))

        request = DummyRequest()
        form = MyForm(object(), request)
        widgets = FormWidgets(form.fields, form, request)
        widgets.fieldset = form.fields

        data, errors = widgets.extract()
        self.assertEqual(len(errors), 2)
        self.assertIsInstance(errors[0], Invalid)
        self.assertIsInstance(errors[1], Invalid)
        self.assertEqual(errors[0].msg, 'error1')
        self.assertEqual(errors[1].msg, 'error2')


class TestFormErrors(BaseTestCase):

    _includes = ['ptah.form']

    def test_form_errors(self):
        from ptah.form import Invalid, TextField
        from ptah.form.form import form_error_message
        request = self.make_request()

        err1 = Invalid('Error1')
        err2 = Invalid('Error2')
        err2.field = TextField('text')

        msg = [err1, err2]

        errs = form_error_message(msg, request)['errors']
        self.assertIn(err1, errs)
        self.assertNotIn(err2, errs)

        request.add_message([err1, err2], 'form:error')

        res = request.render_messages()
        self.assertIn('Please fix indicated errors.', res)

    def test_form_errors_str(self):
        from ptah.form import Invalid, TextField
        from ptah.form.form import form_error_message
        request = self.make_request()

        err1 = 'Error1'
        err2 = Invalid('Error2')
        err2.field = TextField('text')

        msg = [err1, err2]

        errs = form_error_message(msg, request)['errors']
        self.assertIn(err1, errs)
        self.assertNotIn(err2, errs)

        request.add_message(msg, 'form:error')
        res = request.render_messages()
        self.assertIn('Error1', res)
        self.assertIn('Please fix indicated errors.', res)

    def test_add_error_message(self):
        request = self.make_request()

        form = ptah.form.Form(object(), request)

        err = ptah.form.Invalid('Error')
        form.add_error_message([err])

        res = request.render_messages()
        self.assertIn('Please fix indicated errors.', res)


class TestForm(BaseTestCase):

    _includes = ['ptah.form']

    def test_ctor_kwargs(self):
        """ Pass keyword arguments to Form ctor """
        form = ptah.form.Form(object(), DummyRequest(), title='Test Form')
        self.assertEqual('Test Form', form.title)

    def test_ctor_fields(self):
        """ Form ctor converts sequence of fields to Fieldset """
        form = ptah.form.Form(
            object(), DummyRequest(),
            fields=(ptah.form.TextField('firstname'),
                    ptah.form.TextField('lastname')))
        self.assertIsInstance(form.fields, ptah.form.Fieldset)

    def test_ctor_sets_tmpl_widget(self):
        """ Form ctor sets tmpl_widget to all fields """
        form = ptah.form.Form(
            object(), DummyRequest(),
            tmpl_widget='custom:widget',
            fields=ptah.form.Fieldset(
                ptah.form.TextField('firstname'),
                ptah.form.TextField('lastname',tmpl_widget='custom:widget2')))
        self.assertEqual(
            'custom:widget', form.fields['firstname'].cls.tmpl_widget)
        self.assertEqual(
            'custom:widget2', form.fields['lastname'].cls.tmpl_widget)

    def test_ctor_sets_tmpl_widget_recursive(self):
        """ Form ctor sets tmpl_widget to all fields in all fieldsets """
        form = ptah.form.Form(
            object(), DummyRequest(),
            tmpl_widget='custom:widget',
            fields=ptah.form.Fieldset(
                ptah.form.TextField('firstname'),
                ptah.form.Fieldset(ptah.form.TextField('lastname'), name='sub')))
        self.assertEqual(
            'custom:widget', form.fields['firstname'].cls.tmpl_widget)
        self.assertEqual(
            'custom:widget', form.fields['sub']['lastname'].cls.tmpl_widget)

    def test_basics(self):
        request = DummyRequest()
        form = ptah.form.Form(None, request)

        request.url = '/test/form'
        self.assertEqual(form.action, request.url)

        self.assertEqual(form.name, 'form')

        form = ptah.form.Form(None, request)
        form.prefix = 'my.test.form.'
        self.assertEqual(form.name, 'my.test.form')
        self.assertEqual(form.id, 'my-test-form')

    def test_form_content(self):
        request = DummyRequest()
        form = ptah.form.Form(None, request)

        self.assertIsNone(form.form_content())

        form_content = {}
        form.content = form_content
        self.assertIs(form.form_content(), form_content)

    def test_form_content_from_update(self):
        from ptah.form.form import Form

        request = DummyRequest()
        form = Form(None, request)

        form_content = {'test': 'test1'}
        form.update_form(form_content)
        self.assertEqual(form.form_content(), form_content)

    def test_csrf_token(self):
        from ptah.form import form

        class MyForm(form.Form):
            pass

        request = DummyRequest()
        form_ob = MyForm(None, request)

        token = form_ob.csrf_token
        self.assertEqual(token, request.session.get_csrf_token())
        self.assertIsNotNone(token)
        self.assertIsNone(form_ob.validate_csrf_token())

        request.POST = {}

        form_ob.csrf = True
        self.assertRaises(HTTPForbidden, form_ob.validate_csrf_token)
        self.assertRaises(HTTPForbidden, form_ob.validate_form, {}, [])

        request.POST = {form_ob.csrf_name: token}
        self.assertIsNone(form_ob.validate_csrf_token())

    def test_form_params_post(self):
        from ptah.form.form import Form

        form = Form(None, self.request)
        self.assertEqual(form.method, 'post')

        post = {'post': 'info'}
        self.request.POST = post

        self.assertIs(form.form_params(), post)

    def test_form_params_get(self):
        from ptah.form.form import Form

        form = Form(None, self.request)

        get = {'get': 'info'}
        self.request.GET = get
        form.method = 'get'
        self.assertIs(form.form_params(), get)

        form.method = 'unknown'
        self.assertEqual(form.form_params(), None)

    def test_form_convert_params_to_multidict(self):
        from ptah.form.form import Form

        form = Form(None, self.request)

        params = {'params': 'info'}
        form.method = 'POST'
        form.params = params
        self.assertIn('params', form.form_params().keys())
        self.assertIsInstance(form.form_params(), MultiDict)

        params = MultiDict({'params': 'info'})
        form.method = 'POST'
        form.params = params
        self.assertIs(form.form_params(), params)

    def test_form_params_method(self):
        from ptah.form.form import Form

        form = Form(None, None)
        form.method = 'params'
        params = {'post': 'info'}
        form.params = params

        self.assertEqual(list(form.form_params().keys()), ['post'])
        self.assertEqual(list(form.form_params().values()), ['info'])

    def test_form_update_widgets(self):
        import ptah.form

        request = DummyRequest()
        request.POST = {}

        form_ob = ptah.form.Form(None, request)
        form_ob.update_form()

        self.assertIsInstance(form_ob.widgets, ptah.form.FormWidgets)

        form_ob.update_form()
        self.assertEqual(len(form_ob.widgets), 0)

        form_ob.fields = ptah.form.Fieldset(ptah.form.TextField('test'))
        form_ob.update_form()
        self.assertEqual(len(form_ob.widgets), 1)
        self.assertIn('test', form_ob.widgets)
        self.assertIn('test', [f.name for f in form_ob.widgets.fields()])

        self.assertIsInstance(form_ob.widgets['test'], ptah.form.TextField)
        self.assertEqual(form_ob.widgets['test'].name, 'test')
        self.assertEqual(form_ob.widgets['test'].id, 'form-widgets-test')

    def test_form_extract(self):
        import ptah.form

        request = DummyRequest()
        request.POST = {}

        form_ob = ptah.form.Form(None, request)
        form_ob.fields = ptah.form.Fieldset(ptah.form.TextField('test'))
        form_ob.update_form()

        data, errors = form_ob.extract()
        self.assertEqual(errors[0].msg, 'Required')

        request.POST = {'test': 'Test string'}
        form_ob.update_form()
        data, errors = form_ob.extract()
        self.assertEqual(data['test'], 'Test string')

    def test_form_render(self):
        import ptah.form

        request = self.make_request()

        form_ob = ptah.form.Form(None, request)
        form_ob.fields = ptah.form.Fieldset(ptah.form.TextField('test'))
        form_ob.update()

        self.assertIn('<form action="http://example.com"', form_ob.render())

    def test_form_render_bytes(self):
        import ptah.form

        class MyForm(ptah.form.Form):
            def render(self):
                return b'binary'

        form_ob = MyForm(None, self.request)
        form_ob.fields = ptah.form.Fieldset(ptah.form.TextField('test'))
        res = form_ob()

        self.assertIn('binary', res.text)

    def test_form_render_view_config_renderer(self):
        import ptah.form
        request = self.make_request()

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

        self.config.add_view(
            name='test', view=CustomForm,
            renderer='ptah.form:tests/test-form.pt')

        resp = render_view_to_response(None, request, 'test', False).body

        self.assertIn(b'<h1>Custom form</h1>', resp)
        self.assertIn(b'<form action="http://example.com"', resp)

    def test_form_render_view_config(self):
        import ptah.form
        request = self.make_request()

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

        self.config.add_view(name='test', view=CustomForm)

        resp = render_view_to_response(None, request, 'test', False).body
        self.assertIn('<form action="http://example.com"', text_(resp))

    def test_form_render_view_config_return_httpexc(self):
        import ptah.form
        request = self.make_request(POST={'form.buttons.test': 'test'})

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

            @ptah.form.button('test')
            def handler(self):
                return HTTPFound(location='.')

        self.config.add_view(
            name='test', view=CustomForm,
            renderer='ptah.form:tests/test-form.pt')

        resp = render_view_to_response(None, request, 'test', False)
        self.assertIsInstance(resp, HTTPFound)

    def test_form_render_view_config_return_none(self):
        import ptah.form

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

            def update_form(self):
                return

        self.config.add_view(
            name='test', view=CustomForm,
            renderer='ptah.form:tests/test-form.pt')

        resp = render_view_to_response(None, self.request, 'test', False)
        self.assertIn('<h1>Custom form</h1>', str(resp))

    def test_form_render_view_config_layout(self):
        import ptah.form, ptah.renderer
        request = self.make_request()

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

        self.config.add_view(
            name='test', view=CustomForm, renderer=ptah.renderer.layout())
        self.config.add_layout(
            renderer='ptah.form:tests/test-layout.pt')

        resp = render_view_to_response(None, request, 'test', False)
        self.assertIn('<form action="http://example.com"', str(resp))

    def test_form_render_view_config_layout_return_none(self):
        import ptah.form, ptah.renderer
        request = self.make_request()

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

            def update_form(self):
                return

        self.config.add_view(
            name='test', view=CustomForm, renderer=ptah.renderer.layout())
        self.config.add_layout(
            renderer='ptah.form:tests/test-layout.pt')

        resp = render_view_to_response(None, request, 'test', False)
        self.assertIn('<form action="http://example.com"', str(resp))

    def test_form_render_view_config_layout_with_renderer(self):
        import ptah.form, ptah.renderer
        request = self.make_request()

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

        self.config.add_view(
            name='test', view=CustomForm,
            renderer=ptah.renderer.layout('ptah.form:tests/test-form.pt'))
        self.config.add_layout(
            renderer='ptah.form:tests/test-layout.pt')

        resp = render_view_to_response(None, request, 'test', False)
        self.assertIn('Custom form', str(resp))
        self.assertIn('<form action="http://example.com"', str(resp))

    def test_form_render_layout_return_httpexc(self):
        import ptah.form, ptah.renderer
        request = self.make_request(POST={'form.buttons.test': 'test'})

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

            @ptah.form.button('test')
            def handler(self):
                return HTTPFound(location='.')

        self.config.add_view(
            name='test', view=CustomForm,
            renderer=ptah.renderer.layout())
        self.config.add_layout(
            renderer='ptah.form:tests/test-layout.pt')

        resp = render_view_to_response(None, request, 'test', False)
        self.assertIsInstance(resp, HTTPFound)

    def test_form_render_layout_raise_httpexc(self):
        import ptah.form, ptah.renderer
        request = self.make_request(POST={'form.buttons.test': 'test'})

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

            @ptah.form.button('test')
            def handler(self):
                raise HTTPFound(location='.')

        self.config.add_view(
            name='test', view=CustomForm,
            renderer=ptah.renderer.layout())
        self.config.add_layout(
            renderer='ptah.form:tests/test-layout.pt')

        resp = render_view_to_response(None, request, 'test', False)
        self.assertIsInstance(resp, HTTPFound)

    def test_form_render_layout_raise_httpexc_with_template(self):
        import ptah.form, ptah.renderer
        request = self.make_request(POST={'form.buttons.test': 'test'})

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

            @ptah.form.button('test')
            def handler(self):
                raise HTTPFound(location='.')

        self.config.add_view(
            name='test', view=CustomForm,
            renderer=ptah.renderer.layout('ptah.form:tests/test-form.pt'))
        self.config.add_layout(
            renderer='ptah.form:tests/test-layout.pt')

        resp = render_view_to_response(None, request, 'test', False)
        self.assertIsInstance(resp, HTTPFound)

    def test_form_render_view_config_raise_httpexc(self):
        import ptah.form
        request = self.make_request(POST={'form.buttons.test': 'test'})

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

            @ptah.form.button('test')
            def handler(self):
                raise HTTPFound(location='.')

        self.config.add_view(
            name='test', view=CustomForm,
            renderer='ptah.form:tests/test-form.pt')

        resp = render_view_to_response(None, request, 'test', False)
        self.assertIsInstance(resp, HTTPFound)

    def test_form_action_return_httpexc(self):
        import ptah.form
        request = self.make_request(POST={'form.buttons.test': 'test'})

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

            @ptah.form.button('test')
            def handler(self):
                return HTTPFound(location='.')

        res = CustomForm(object(), request)()
        self.assertIsInstance(res, HTTPFound)

    def test_form_action_raise_httpexc(self):
        import ptah.form
        request = self.make_request(POST={'form.buttons.test': 'test'})

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

            @ptah.form.button('test')
            def handler(self):
                raise HTTPFound(location='.')

        res = CustomForm(object(), request)()
        self.assertIsInstance(res, HTTPFound)

    def test_update_return_response(self):
        import ptah.form
        request = self.make_request()
        response = request.response

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

            def update(self):
                return response

        res = CustomForm(object(), request)()
        self.assertIs(res, response)

    def test_update_form(self):
        import ptah.form
        request = self.make_request()

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

            def update(self):
                return {1: 'test'}

        form = CustomForm(object(), request)

        res = form.update_form()
        self.assertEqual(res, {1: 'test'})

    def test_update_form_return_response(self):
        import ptah.form
        request = self.make_request()

        resp = HTTPFound()

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

            def update_form(self):
                return resp

        res = CustomForm(object(), request)()
        self.assertIs(res, resp)

    def test_update_form_action_return_dict(self):
        import ptah.form
        request = self.make_request(POST={'form.buttons.test': 'test'})

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

            def update(self):
                return None

            @ptah.form.button('test')
            def test_handler(self):
                return {1: 'test'}

        form = CustomForm(object(), request)

        res = form.update_form()
        self.assertEqual(res, {1: 'test'})

    def test_update_form_action_return_dict_combine_with_update(self):
        import ptah.form
        request = self.make_request(POST={'form.buttons.test': 'test'})

        class CustomForm(ptah.form.Form):
            fields = ptah.form.Fieldset(ptah.form.TextField('test'))

            def update(self):
                return {0: '0'}

            @ptah.form.button('test')
            def test_handler(self):
                return {1: 'test'}

        form = CustomForm(object(), request)

        res = form.update_form()
        self.assertEqual(res, {0: '0', 1: 'test'})

    def test_validate(self):
        from ptah.form import Invalid, Form

        class MyForm(Form):
            def validate(self, data, errors):
                errors.append(Invalid('error1'))

        form = MyForm(object(), self.request)

        errors = []
        form.validate({}, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].msg, 'error1')

    def test_validate_form(self):
        from ptah.form import Invalid, Form

        class MyForm(Form):
            def validate(self, data, errors):
                errors.append(Invalid('error1'))

        form = MyForm(object(), self.request)

        errors = []
        form.validate_form({}, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].msg, 'error1')

    def test_validate_form_raise(self):
        from ptah.form import Invalid, Form

        class MyForm(Form):
            def validate(self, data, errors):
                raise Invalid('error1')

        form = MyForm(object(), self.request)

        errors = []
        form.validate_form({}, errors)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].msg, 'error1')
