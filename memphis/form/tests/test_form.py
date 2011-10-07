import unittest

class TestFormWidgets(unittest.TestCase):
    def _makeOne(self, fields, form, request):
        from memphis.form.form import FormWidgets
        return FormWidgets(fields, form, request)

    def test_ctor(self):
        request = DummyRequest()
        form = DummyForm()
        fields = DummyFields()
        inst = self._makeOne(fields, form, request)
        self.assertEqual(inst.fields, fields)
        self.assertEqual(inst.form, form)
        self.assertEqual(inst.request, request)



class DummyRequest(object):
    def __init__(self):
        self.params = {}
        self.cookies = {}
        
class DummyForm(object):
    prefix = 'prefix'
    def getParams(self): # pragma: no cover
        return None
    def getContent(self): # pragma: no cover
        return None

class DummyFieldset(object):
    def fieldsets(self): # pragma: no cover
        return []

class DummyFields(object):
    def __init__(self, fieldset=None):
        if fieldset is None:
            fieldset = DummyFieldset()
        self.fieldset = fieldset
        
    def bind(self, content, params): # pragma: no cover
        self.content = content
        self.params = params
        return self.fieldset
    

