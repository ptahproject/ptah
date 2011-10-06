import unittest

class TestFormWidgets(unittest.TestCase):
    def _makeOne(self, fields, form, request):
        from memphis.form.form import FormWidgets
        return FormWidgets(fields, form, request)

    def test_ctor(self):
        from pyramid.i18n import Localizer
        request = DummyRequest()
        form = DummyForm()
        fields = DummyFields()
        inst = self._makeOne(fields, form, request)
        self.assertEqual(inst.fields, fields)
        self.assertEqual(inst.form, form)
        self.assertEqual(inst.request, request)
        self.assertEqual(inst.localizer.__class__, Localizer)

class DummyRequest(object):
    def __init__(self):
        self.params = {}
        self.cookies = {}
        
class DummyForm(object):
    prefix = 'prefix'
    def getParams(self):
        return None
    def getContent(self):
        return None

class DummyFieldset(object):
    def fieldsets(self):
        return []

class DummyFields(object):
    def __init__(self, fieldset=None):
        if fieldset is None:
            fieldset = DummyFieldset()
        self.fieldset = fieldset
        
    def bind(self, content, params):
        self.content = content
        self.params = params
        return self.fieldset
    

