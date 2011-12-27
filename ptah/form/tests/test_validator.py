from ptah.testing import TestCase


def invalid_exc(func, *arg, **kw):
    from ptah.form import Invalid
    try:
        func(*arg, **kw)
    except Invalid as e:
        return e
    else:
        raise AssertionError('Invalid not raised') # pragma: no cover


class DummyValidator(object):
    def __init__(self, msg=None):
        self.msg = msg

    def __call__(self, node, value):
        from ptah.form import Invalid
        if self.msg:
            raise Invalid(node, self.msg)


class TestAll(TestCase):
    def _makeOne(self, validators):
        from ptah.form import All
        return All(*validators)

    def test_success(self):
        validator1 = DummyValidator()
        validator2 = DummyValidator()
        validator = self._makeOne([validator1, validator2])
        self.assertEqual(validator(None, None), None)

    def test_failure(self):
        validator1 = DummyValidator('msg1')
        validator2 = DummyValidator('msg2')
        validator = self._makeOne([validator1, validator2])
        e = invalid_exc(validator, None, None)
        self.assertEqual(e.msg, ['msg1', 'msg2'])


class TestFunction(TestCase):
    def _makeOne(self, *arg, **kw):
        from ptah.form import Function
        return Function(*arg, **kw)

    def test_success_function_returns_True(self):
        validator = self._makeOne(lambda x: True)
        self.assertEqual(validator(None, None), None)

    def test_fail_function_returns_empty_string(self):
        validator = self._makeOne(lambda x: '')
        e = invalid_exc(validator, None, None)
        self.assertEqual(e.msg, 'Invalid value')

    def test_fail_function_returns_False(self):
        validator = self._makeOne(lambda x: False)
        e = invalid_exc(validator, None, None)
        self.assertEqual(e.msg, 'Invalid value')

    def test_fail_function_returns_string(self):
        validator = self._makeOne(lambda x: 'fail')
        e = invalid_exc(validator, None, None)
        self.assertEqual(e.msg, 'fail')

    def test_propagation(self):
        validator = self._makeOne(lambda x: 'a' in x, 'msg')
        self.assertRaises(TypeError, validator, None, None)

class TestRange(TestCase):
    def _makeOne(self, **kw):
        from ptah.form import Range
        return Range(**kw)

    def test_success_no_bounds(self):
        validator = self._makeOne()
        self.assertEqual(validator(None, 1), None)

    def test_success_upper_bound_only(self):
        validator = self._makeOne(max=1)
        self.assertEqual(validator(None, -1), None)

    def test_success_minimum_bound_only(self):
        validator = self._makeOne(min=0)
        self.assertEqual(validator(None, 1), None)

    def test_success_min_and_max(self):
        validator = self._makeOne(min=1, max=1)
        self.assertEqual(validator(None, 1), None)

    def test_min_failure(self):
        validator = self._makeOne(min=1)
        e = invalid_exc(validator, None, 0)
        self.assertEqual(e.msg.interpolate(), '0 is less than minimum value 1')

    def test_min_failure_msg_override(self):
        validator = self._makeOne(min=1, min_err='wrong')
        e = invalid_exc(validator, None, 0)
        self.assertEqual(e.msg, 'wrong')

    def test_max_failure(self):
        validator = self._makeOne(max=1)
        e = invalid_exc(validator, None, 2)
        self.assertEqual(e.msg.interpolate(),
                         '2 is greater than maximum value 1')

    def test_max_failure_msg_override(self):
        validator = self._makeOne(max=1, max_err='wrong')
        e = invalid_exc(validator, None, 2)
        self.assertEqual(e.msg, 'wrong')

class TestRegex(TestCase):
    def _makeOne(self, pattern):
        from ptah.form import Regex
        return Regex(pattern)

    def test_valid_regex(self):
        self.assertEqual(self._makeOne('a')(None, 'a'), None)
        self.assertEqual(self._makeOne('[0-9]+')(None, '1111'), None)
        self.assertEqual(self._makeOne('')(None, ''), None)
        self.assertEqual(self._makeOne('.*')(None, ''), None)

    def test_invalid_regexs(self):
        from ptah.form import Invalid
        self.assertRaises(Invalid, self._makeOne('[0-9]+'), None, 'a')
        self.assertRaises(Invalid, self._makeOne('a{2,4}'), None, 'ba')

    def test_regex_not_string(self):
        from ptah.form import Invalid
        import re
        regex = re.compile('[0-9]+')
        self.assertEqual(self._makeOne(regex)(None, '01'), None)
        self.assertRaises(Invalid, self._makeOne(regex), None, 't')


class TestEmail(TestCase):
    def _makeOne(self):
        from ptah.form import Email
        return Email()

    def test_valid_emails(self):
        validator = self._makeOne()
        self.assertEqual(validator(None, 'me@here.com'), None)
        self.assertEqual(validator(None, 'me1@here1.com'), None)
        self.assertEqual(validator(None, 'name@here1.us'), None)
        self.assertEqual(validator(None, 'name@here1.info'), None)
        self.assertEqual(validator(None, 'foo@bar.baz.biz'), None)

    def test_empty_email(self):
        validator = self._makeOne()
        e = invalid_exc(validator, None, '')
        self.assertEqual(e.msg, 'Invalid email address')

    def test_invalid_emails(self):
        validator = self._makeOne()
        from ptah.form import Invalid
        self.assertRaises(Invalid, validator, None, 'me@here.')
        self.assertRaises(Invalid, validator, None, 'name@here.comcom')
        self.assertRaises(Invalid, validator, None, '@here.us')
        self.assertRaises(Invalid, validator, None, '(name)@here.info')

class TestLength(TestCase):
    def _makeOne(self, min=None, max=None):
        from ptah.form import Length
        return Length(min=min, max=max)

    def test_success_no_bounds(self):
        validator = self._makeOne()
        self.assertEqual(validator(None, ''), None)

    def test_success_upper_bound_only(self):
        validator = self._makeOne(max=1)
        self.assertEqual(validator(None, 'a'), None)

    def test_success_minimum_bound_only(self):
        validator = self._makeOne(min=0)
        self.assertEqual(validator(None, ''), None)

    def test_success_min_and_max(self):
        validator = self._makeOne(min=1, max=1)
        self.assertEqual(validator(None, 'a'), None)

    def test_min_failure(self):
        validator = self._makeOne(min=1)
        e = invalid_exc(validator, None, '')
        self.assertEqual(e.msg.interpolate(), 'Shorter than minimum length 1')

    def test_max_failure(self):
        validator = self._makeOne(max=1)
        e = invalid_exc(validator, None, 'ab')
        self.assertEqual(e.msg.interpolate(), 'Longer than maximum length 1')

class TestOneOf(TestCase):
    def _makeOne(self, values):
        from ptah.form import OneOf
        return OneOf(values)

    def test_success(self):
        validator = self._makeOne([1])
        self.assertEqual(validator(None, 1), None)

    def test_failure(self):
        validator = self._makeOne([1, 2])
        e = invalid_exc(validator, None, None)
        self.assertEqual(e.msg.interpolate(), '"None" is not one of 1, 2')
