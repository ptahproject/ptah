import decimal
from memphis import form
from base import Base

class DummyRequest(object):
    def __init__(self):
        self.params = {}
        self.cookies = {}
        

def strip(str):
    return ' '.join(s.strip() for s in str.split())


class TestTextField(Base):

    def _makeOne(self, name, **kw):
        return form.TextField(name, **kw)

    def test_fields_text(self):
        request = DummyRequest()

        field = self._makeOne('test')
        field = field.bind('', u'content', {})
        field.update(request)

        self.assertEqual(field.serialize(u'value'), u'value')
        self.assertEqual(field.deserialize(u'value'), u'value')
        
        self.assertEqual(strip(field.render(request)),
                         '<input type="text" name="test" title="Test" value="content" class="text-widget" />')

        field.mode = form.FORM_DISPLAY
        self.assertEqual(strip(field.render(request)),
                         '<span class="uneditable-input"> <span title="Test" class="text-widget"> content </span> </span>')

        
        field = self._makeOne('test')
        field = field.bind('', u'content', {'test': 'form'})
        field.update(request)

        self.assertEqual(strip(field.render(request)),
                         '<input type="text" name="test" title="Test" value="form" class="text-widget" />')

        field.mode = form.FORM_DISPLAY
        self.assertEqual(strip(field.render(request)),
                         '<span class="uneditable-input"> <span title="Test" class="text-widget"> form </span> </span>')


class TestIntegerField(Base):

    def _makeOne(self, name, **kw):
        return form.IntegerField(name, **kw)

    def test_fields_int(self):
        request = DummyRequest()

        field = self._makeOne('test')
        field = field.bind('', 10, {})
        field.update(request)

        self.assertIs(field.serialize(form.null), form.null)
        self.assertEqual(field.serialize(10), '10')
        self.assertRaises(form.Invalid, field.serialize, u'value')

        self.assertIs(field.deserialize(''), form.null)
        self.assertEqual(field.deserialize('10'), 10)
        self.assertRaises(form.Invalid, field.deserialize, u'value')

        self.assertEqual(
            strip(field.render(request)),
            '<input type="text" name="test" title="Test" value="10" class="int-widget" />')

class TestFloatField(Base):

    def _makeOne(self, name, **kw):
        return form.FloatField(name, **kw)

    def test_fields_float(self):
        request = DummyRequest()

        field = self._makeOne('test')
        field = field.bind('', 10.34, {})
        field.update(request)

        self.assertIs(field.serialize(form.null), form.null)
        self.assertEqual(field.serialize(10.34), '10.34')
        self.assertRaises(form.Invalid, field.serialize, u'value')

        self.assertIs(field.deserialize(''), form.null)
        self.assertEqual(field.deserialize('10.34'), 10.34)
        self.assertRaises(form.Invalid, field.deserialize, u'value')

        self.assertEqual(
            strip(field.render(request)),
            '<input type="text" name="test" title="Test" value="10.34" class="float-widget" />')


class TestDeciamlField(Base):

    def _makeOne(self, name, **kw):
        return form.DecimalField(name, **kw)

    def test_fields_decimal(self):
        request = DummyRequest()

        field = self._makeOne('test')
        field = field.bind('', decimal.Decimal('10.34'), {})
        field.update(request)

        self.assertIs(field.serialize(form.null), form.null)
        self.assertEqual(field.serialize(decimal.Decimal('10.34')), '10.34')
        self.assertRaises(form.Invalid, field.serialize, u'value')

        self.assertIs(field.deserialize(''), form.null)
        self.assertEqual(field.deserialize('10.34'), decimal.Decimal('10.34'))
        self.assertRaises(form.Invalid, field.deserialize, u'value')

        self.assertEqual(
            strip(field.render(request)),
            '<input type="text" name="test" title="Test" value="10.34" class="decimal-widget" />')


class TestLinesField(Base):

    def _makeOne(self, name, **kw):
        return form.LinesField(name, **kw)

    def test_fields_decimal(self):
        request = DummyRequest()

        field = self._makeOne('test')
        field = field.bind('', ['1','2','3'], {})
        field.update(request)

        self.assertIs(field.serialize(form.null), form.null)
        self.assertEqual(field.serialize(['1','2','3']), '1\n2\n3')
        self.assertRaises(form.Invalid, field.serialize, 1)

        self.assertIs(field.deserialize(''), form.null)
        self.assertEqual(field.deserialize('1\n2\n3'), ['1','2','3'])
        self.assertRaises(form.Invalid, field.deserialize, 5)

        self.assertEqual(
            strip(field.render(request)),
            '<textarea rows="5" name="test" title="Test" cols="40" class="textlines-widget">1 2 3</textarea>')


class TestCheckboxsField(Base):

    def _makeOne(self, name, **kw):
        return form.CheckboxsField(name, **kw)

    def test_fields_decimal(self):
        request = DummyRequest()

        field = self._makeOne('test')
        field = field.bind('', [1,2,3], {})
        #field.update(request)

        #self.assertIs(field.serialize(form.null), form.null)
        #self.assertEqual(field.serialize([1,2,3]), ['1','2','3'])
        #self.assertRaises(form.Invalid, field.serialize, 1)

        #self.assertIs(field.deserialize(''), form.null)
        #self.assertEqual(field.deserialize(['1','2','3']), [1,2,3])
        #self.assertRaises(form.Invalid, field.deserialize, 5)

        #self.assertEqual(
        #    strip(field.render(request)),
        #    '<textarea rows="5" name="test" title="Test" cols="40" class="textlines-widget">1 2 3</textarea>')

