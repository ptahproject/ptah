from ptah.testing import PtahTestCase, TestCase
from webob.multidict import MultiDict
from pyramid.compat import text_
from pyramid.view import view_config, render_view_to_response
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound, HTTPForbidden


class TestFormWidgets(TestCase):
    def _makeOne(self, fields, form, request):
        from ptah.form.form import FormWidgets
        return FormWidgets(fields, form, request)

    def test_ctor(self):
        request = DummyRequest()
        form = DummyForm()
        fields = DummyFields()
        inst = self._makeOne(fields, form, request)
        self.assertEqual(inst.form_fields, fields)
        self.assertEqual(inst.form, form)
        self.assertEqual(inst.request, request)


class TestFormErrors(PtahTestCase):

    def test_form_errors(self):
        import ptah
        from ptah.form import Invalid, TextField
        from ptah.form.form import formErrorMessage
        request = DummyRequest()

        err1 = Invalid(None, 'Error1')
        err2 = Invalid(None, 'Error2')
        err2.field = TextField('text')

        msg = ptah.view.Message([err1, err2], request)

        errs = formErrorMessage(msg, request)['errors']
        self.assertIn(err1, errs)
        self.assertNotIn(err2, errs)

        ptah.view.add_message(request, [err1, err2], 'form-error')

        res = ptah.view.render_messages(request)
        self.assertIn('Please fix indicated errors.', res)


class TestForm(PtahTestCase):

    def test_basics(self):
        from ptah.form.form import Form

        request = DummyRequest()
        form = Form(None, request)

        request.url = '/test/form'
        self.assertEqual(form.action, request.url)

        self.assertEqual(form.name, 'form')

        form = Form(None, request)
        form.prefix = 'my.test.form.'
        self.assertEqual(form.name, 'my.test.form')

        self.assertEqual(form.id, 'my-test-form')

    def test_form_content(self):
        from ptah.form.form import Form

        request = DummyRequest()
        form = Form(None, request)

        self.assertIsNone(form.form_content())

        form_content = {}
        form.content = form_content
        self.assertIs(form.form_content(), form_content)

    def test_form_content_from_update(self):
        from ptah.form.form import Form

        request = DummyRequest()
        form = Form(None, request)

        form_content = {'test': 'test1'}
        form.update(**form_content)
        self.assertEqual(form.form_content(), form_content)

    def test_csrf_token(self):
        from ptah.form import form

        class MyForm(form.Form):
            pass

        request = DummyRequest()
        form_ob = MyForm(None, request)

        token = form_ob.token
        self.assertEqual(token, request.session.get_csrf_token())
        self.assertIsNotNone(token)
        self.assertIsNone(form_ob.validate_csrf_token())

        request.POST = {}

        form_ob.csrf = True
        self.assertRaises(HTTPForbidden, form_ob.validate_csrf_token)
        self.assertRaises(HTTPForbidden, form_ob.validate, {}, [])

        request.POST = {form_ob.csrfname: token}
        self.assertIsNone(form_ob.validate_csrf_token())

    def test_form_params(self):
        from ptah.form.form import Form, DisplayForm

        request = DummyRequest()

        form = Form(None, request)
        disp_form = DisplayForm(None, request)

        self.assertEqual(form.method, 'post')

        post = {'post': 'info'}
        request.POST = post

        self.assertIs(form.form_params(), post)
        self.assertIs(disp_form.form_params(), DisplayForm.params)

        get = {'get': 'info'}
        request.GET = get
        form.method = 'get'
        self.assertIs(form.form_params(), get)

        form.method = 'unknown'
        self.assertEqual(form.form_params(), None)

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

    def test_form_mode(self):
        from ptah.form.form import Form, DisplayForm, \
            FORM_INPUT, FORM_DISPLAY

        request = DummyRequest()

        form = Form(None, request)
        self.assertEqual(form.mode, FORM_INPUT)

        form = DisplayForm(None, request)
        self.assertEqual(form.mode, FORM_DISPLAY)

    def test_form_update_widgets(self):
        from ptah import form

        request = DummyRequest()
        request.POST = {}

        form_ob = form.Form(None, request)
        form_ob.update()

        self.assertIsInstance(form_ob.widgets, form.FormWidgets)
        self.assertEqual(form_ob.widgets.mode, form_ob.mode)

        form_ob.mode = form.FORM_DISPLAY
        form_ob.update()
        self.assertEqual(form_ob.widgets.mode, form.FORM_DISPLAY)

        self.assertEqual(len(form_ob.widgets), 0)

        form_ob.fields = form.Fieldset(form.TextField('test'))
        form_ob.update()
        self.assertEqual(len(form_ob.widgets), 1)
        self.assertIn('test', form_ob.widgets)
        self.assertIn('test', [f.name for f in form_ob.widgets.fields()])

        self.assertIsInstance(form_ob.widgets['test'], form.TextField)
        self.assertEqual(form_ob.widgets['test'].name, 'test')
        self.assertEqual(form_ob.widgets['test'].id, 'form-widgets-test')

    def test_form_extract(self):
        from ptah import form

        request = DummyRequest()
        request.POST = {}

        form_ob = form.Form(None, request)
        form_ob.fields = form.Fieldset(form.TextField('test'))
        form_ob.update()

        data, errors = form_ob.extract()
        self.assertEqual(errors[0].msg, 'Required')

        request.POST = {'test': 'Test string'}
        form_ob.update()
        data, errors = form_ob.extract()
        self.assertEqual(data['test'], 'Test string')

    def test_form_render(self):
        from ptah import form

        request = DummyRequest()

        form_ob = form.Form(None, request)
        form_ob.fields = form.Fieldset(form.TextField('test'))
        form_ob.update()

        self.assertIn('<form action="http://example.com"', form_ob.render())

    def test_form_render_view_config_renderer(self):
        from ptah import form
        request = DummyRequest()

        class CustomForm(form.Form):
            fields = form.Fieldset(form.TextField('test'))

        self.config.add_view(
            name='test', view=CustomForm,
            renderer='ptah.form:tests/test-form.pt')

        resp = render_view_to_response(None, request, 'test', False).body

        self.assertIn(b'<h1>Custom form</h1>', resp)
        self.assertIn(b'<form action="http://example.com"', resp)

    def test_form_render_view_config(self):
        from ptah import form
        request = DummyRequest()

        class CustomForm(form.Form):
            fields = form.Fieldset(form.TextField('test'))

        self.config.add_view(name='test', view=CustomForm)

        resp = render_view_to_response(None, request, 'test', False).body
        self.assertIn('<form action="http://example.com"', text_(resp))

    def test_form_render_view_config_return(self):
        from ptah import form
        request = DummyRequest(POST={'form.buttons.test': 'test'})

        class CustomForm(form.Form):
            fields = form.Fieldset(form.TextField('test'))

            @form.button('test')
            def handler(self):
                return HTTPFound(location='.')

        res = CustomForm(object(), request)()
        self.assertIsInstance(res, HTTPFound)


class DummyForm(object):
    prefix = 'prefix'
    def form_params(self): # pragma: no cover
        return None
    def form_content(self): # pragma: no cover
        return None


class DummyFieldset(object):
    def fieldsets(self): # pragma: no cover
        return []


class DummyFields(object):
    def __init__(self, fieldset=None):
        if fieldset is None:
            fieldset = DummyFieldset()
        self.fieldset = fieldset

    def bind(self, data, params): # pragma: no cover
        self.data = data
        self.params = params
        return self.fieldset
