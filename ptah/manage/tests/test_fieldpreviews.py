import ptah
import ptah.form
from ptah.form.directives import ID_PREVIEW
from ptah.manage import fieldpreviews
from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest
from pyramid.view import render_view_to_response


class TestFieldPreviews(PtahTestCase):

    def test_multiChoicePreview(self):
        previews = self.registry[ID_PREVIEW]
        self.assertIs(previews[ptah.form.MultiChoiceField],
                      fieldpreviews.multiChoicePreview)

        request = DummyRequest()
        html = fieldpreviews.multiChoicePreview(request)
        self.assertIn('Multi choice field', html)

    def test_choicePreview(self):
        previews = self.registry[ID_PREVIEW]
        self.assertIs(previews[ptah.form.ChoiceField],
                      fieldpreviews.choicePreview)

        request = DummyRequest()
        html = fieldpreviews.choicePreview(request)
        self.assertIn('Choice field', html)

    def test_boolPreview(self):
        previews = self.registry[ID_PREVIEW]
        self.assertIs(previews[ptah.form.BoolField],
                      fieldpreviews.boolPreview)

        request = DummyRequest()
        html = fieldpreviews.boolPreview(request)
        self.assertIn('Boolean field', html)

    def test_radioPreview(self):
        previews = self.registry[ID_PREVIEW]
        self.assertIs(previews[ptah.form.RadioField],
                      fieldpreviews.radioPreview)

        request = DummyRequest()
        html = fieldpreviews.radioPreview(request)
        self.assertIn('Radio field', html)

    def test_textareaPreview(self):
        previews = self.registry[ID_PREVIEW]
        self.assertIs(previews[ptah.form.TextAreaField],
                      fieldpreviews.textareaPreview)

        request = DummyRequest()
        html = fieldpreviews.textareaPreview(request)
        self.assertIn('TextArea field', html)

    def test_linesPreview(self):
        previews = self.registry[ID_PREVIEW]
        self.assertIs(previews[ptah.form.LinesField],
                      fieldpreviews.linesPreview)

        request = DummyRequest()
        html = fieldpreviews.linesPreview(request)
        self.assertIn('Lines field', html)

    def test_textPreview(self):
        previews = self.registry[ID_PREVIEW]
        self.assertIs(previews[ptah.form.TextField],
                      fieldpreviews.textPreview)

        request = DummyRequest()
        html = fieldpreviews.textPreview(request)
        self.assertIn('Text field', html)

    def test_intPreview(self):
        previews = self.registry[ID_PREVIEW]
        self.assertIs(previews[ptah.form.IntegerField],
                      fieldpreviews.intPreview)

        request = DummyRequest()
        html = fieldpreviews.intPreview(request)
        self.assertIn('Integer field', html)

    def test_floatPreview(self):
        previews = self.registry[ID_PREVIEW]
        self.assertIs(previews[ptah.form.FloatField],
                      fieldpreviews.floatPreview)

        request = DummyRequest()
        html = fieldpreviews.floatPreview(request)
        self.assertIn('Float field', html)

    def test_decimalPreview(self):
        previews = self.registry[ID_PREVIEW]
        self.assertIs(previews[ptah.form.DecimalField],
                      fieldpreviews.decimalPreview)

        request = DummyRequest()
        html = fieldpreviews.decimalPreview(request)
        self.assertIn('Decimal field', html)

    def test_passwordPreview(self):
        previews = self.registry[ID_PREVIEW]
        self.assertIs(previews[ptah.form.PasswordField],
                      fieldpreviews.passwordPreview)

        request = DummyRequest()
        html = fieldpreviews.passwordPreview(request)
        self.assertIn('Password field', html)

    def test_timezonePreview(self):
        previews = self.registry[ID_PREVIEW]
        self.assertIs(previews[ptah.form.TimezoneField],
                      fieldpreviews.timezonePreview)

        request = DummyRequest()
        html = fieldpreviews.timezonePreview(request)
        self.assertIn('Timezone field', html)


class TestFieldsModule(PtahTestCase):

    def test_fields_module(self):
        from ptah.manage.manage import PtahManageRoute
        from ptah.manage.fields import FieldsModule

        request = self.request

        ptah.auth_service.set_userid('test')
        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)
        cfg['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['fields']

        self.assertIsInstance(mod, FieldsModule)

    def test_fields_view(self):
        from ptah.manage.fields import FieldsModule, FieldsView

        request = self.request

        mod = FieldsModule(None, request)

        res = render_view_to_response(mod, request, '', False)
        self.assertEqual(res.status, '200 OK')

        from ptah.form.directives import ID_FIELD

        fields = self.registry[ID_FIELD]

        view = FieldsView(None, request)
        view.update()

        self.assertEqual(len(view.fields), len(fields))
        self.assertIn('name', view.fields[0])
        self.assertIn('preview', view.fields[0])
