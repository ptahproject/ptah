import transaction
import ptah, ptah_crowd
from memphis import config
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

from memphis import form
from memphis.form.field import previews
from ptah_modules import fieldpreviews

from base import Base


class TestFieldPreviews(Base):

    def test_multiChoicePreview(self):
        self.assertIs(previews[form.MultiChoiceField],
                      fieldpreviews.multiChoicePreview)
        
        request = DummyRequest()
        html = fieldpreviews.multiChoicePreview(request)
        self.assertIn('Multi choice field', html)

    def test_choicePreview(self):
        self.assertIs(previews[form.ChoiceField],
                      fieldpreviews.choicePreview)
        
        request = DummyRequest()
        html = fieldpreviews.choicePreview(request)
        self.assertIn('Choice field', html)

    def test_boolPreview(self):
        self.assertIs(previews[form.BoolField],
                      fieldpreviews.boolPreview)
        
        request = DummyRequest()
        html = fieldpreviews.boolPreview(request)
        self.assertIn('Boolean field', html)

    def test_radioPreview(self):
        self.assertIs(previews[form.RadioField],
                      fieldpreviews.radioPreview)
        
        request = DummyRequest()
        html = fieldpreviews.radioPreview(request)
        self.assertIn('Radio field', html)

    def test_textareaPreview(self):
        self.assertIs(previews[form.TextAreaField],
                      fieldpreviews.textareaPreview)
        
        request = DummyRequest()
        html = fieldpreviews.textareaPreview(request)
        self.assertIn('TextArea field', html)

    def test_linesPreview(self):
        self.assertIs(previews[form.LinesField],
                      fieldpreviews.linesPreview)
        
        request = DummyRequest()
        html = fieldpreviews.linesPreview(request)
        self.assertIn('Lines field', html)

    def test_textPreview(self):
        self.assertIs(previews[form.TextField],
                      fieldpreviews.textPreview)
        
        request = DummyRequest()
        html = fieldpreviews.textPreview(request)
        self.assertIn('Text field', html)

    def test_intPreview(self):
        self.assertIs(previews[form.IntegerField],
                      fieldpreviews.intPreview)
        
        request = DummyRequest()
        html = fieldpreviews.intPreview(request)
        self.assertIn('Integer field', html)

    def test_floatPreview(self):
        self.assertIs(previews[form.FloatField],
                      fieldpreviews.floatPreview)
        
        request = DummyRequest()
        html = fieldpreviews.floatPreview(request)
        self.assertIn('Float field', html)

    def test_decimalPreview(self):
        self.assertIs(previews[form.DecimalField],
                      fieldpreviews.decimalPreview)
        
        request = DummyRequest()
        html = fieldpreviews.decimalPreview(request)
        self.assertIn('Decimal field', html)

    def test_passwordPreview(self):
        self.assertIs(previews[form.PasswordField],
                      fieldpreviews.passwordPreview)
        
        request = DummyRequest()
        html = fieldpreviews.passwordPreview(request)
        self.assertIn('Password field', html)


class TestFieldsModule(Base):

    def test_fields_module(self):
        from ptah.manage import PtahManageRoute
        from ptah_modules.fields import FieldsModule
        
        request = DummyRequest()

        ptah.authService.set_userid('test')
        ptah.PTAH_CONFIG['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['fields']

        self.assertIsInstance(mod, FieldsModule)

    def test_fields_view(self):
        from ptah_modules.fields import FieldsModule, FieldsView
        
        request = DummyRequest()

        mod = FieldsModule(None, request)

        res = FieldsView.__renderer__(mod, request)
        self.assertEqual(res.status, '200 OK')

        from memphis.form.field import fields, previews

        view = FieldsView(None, request)
        view.update()

        self.assertEqual(len(view.fields), len(fields))
        self.assertIn('name', view.fields[0])
        self.assertIn('preview', view.fields[0])
