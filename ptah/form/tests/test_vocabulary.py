"""Test of the Vocabulary and related support APIs."""
from ptah.form import vocabulary
from ptah.testing import TestCase


class VocabularyTests(TestCase):

    list_vocab = vocabulary.Vocabulary(1, 2, 3)
    items_vocab = vocabulary.Vocabulary(
        (1, 'one'), (2, 'two'), (3, 'three'), (4, 'fore!'))

    def test_ctor_from_strings(self):
        """ Create vocabulary from strings """
        voc = vocabulary.Vocabulary('one', 'two')

        self.assertEqual(2, len(voc))
        self.assertIn('one', voc)

        term = voc.get_term('two')
        self.assertEqual(term.value, 'two')
        self.assertEqual(term.token, 'two')
        self.assertEqual(term.title, 'two')

    def test_ctor_from_other(self):
        """ Create vocabulary from integers """
        voc = vocabulary.Vocabulary(1, 2)

        self.assertEqual(2, len(voc))
        self.assertIn(1, voc)

        term = voc.get_term(2)
        self.assertEqual(term.value, 2)
        self.assertEqual(term.token, '2')
        self.assertEqual(term.title, '2')

    def test_ctor_from_2_tuple(self):
        """ Create vocabulary from list of 2 items tuples """
        voc = vocabulary.Vocabulary((1,'one'), (2,'two'))

        self.assertEqual(2, len(voc))
        self.assertIn(1, voc)

        term = voc.get_term(2)
        self.assertEqual(term.value, 2)
        self.assertEqual(term.token, 'two')
        self.assertEqual(term.title, 'two')

    def test_ctor_from_3_tuple(self):
        """ Create vocabulary from list of 3 items tuples """
        voc = vocabulary.Vocabulary((1,'one','One'), (2,'two','Two'))

        self.assertEqual(2, len(voc))
        self.assertIn(1, voc)

        term = voc.get_term(2)
        self.assertEqual(term.value, 2)
        self.assertEqual(term.token, 'two')
        self.assertEqual(term.title, 'Two')

    def test_ctor_from_4_tuple(self):
        """ Create vocabulary from list of 4 items tuples """
        voc = vocabulary.Vocabulary(
            (1,'one','One','One d'), (2,'two','Two','Two desc'))

        self.assertEqual(2, len(voc))
        self.assertIn(1, voc)

        term = voc.get_term(2)
        self.assertEqual(term.value, 2)
        self.assertEqual(term.token, 'two')
        self.assertEqual(term.title, 'Two')
        self.assertEqual(term.description, 'Two desc')

    def test_ctor_from_terms(self):
        """ Create vocabulary from list of 4 items tuples """
        voc = vocabulary.Vocabulary(
            vocabulary.Term(1,'one','One','One d'),
            vocabulary.Term(2,'two','Two','Two desc'))

        self.assertEqual(2, len(voc))
        self.assertIn(1, voc)

        term = voc.get_term(2)
        self.assertEqual(term.value, 2)
        self.assertEqual(term.token, 'two')
        self.assertEqual(term.title, 'Two')
        self.assertEqual(term.description, 'Two desc')

    def test_term_ctor(self):
        t = vocabulary.Term(1)
        self.assertEqual(t.value, 1)
        self.assertEqual(t.token, "1")
        t = vocabulary.Term(1, "One")
        self.assertEqual(t.value, 1)
        self.assertEqual(t.token, "One")
        self.assertEqual(repr(t), 'Term<"1:One:1">')

    def test_term_ctor_title(self):
        t = vocabulary.Term(1)
        self.assertEqual(t.title, '1')
        t = vocabulary.Term(1, title="Title")
        self.assertEqual(t.title, "Title")

    def test_order(self):
        value = 1
        for t in self.list_vocab:
            self.assertEqual(t.value, value)
            value += 1

        value = 1
        for t in self.items_vocab:
            self.assertEqual(t.value, value)
            value += 1

    def test_len(self):
        self.assertEqual(len(self.list_vocab), 3)
        self.assertEqual(len(self.items_vocab), 4)

    def test_contains(self):
        for v in (self.list_vocab, self.items_vocab):
            self.assert_(1 in v and 2 in v and 3 in v)
            self.assert_(5 not in v)

        self.assertNotIn([500], self.items_vocab)

    def test_iter_and_get_term(self):
        for v in (self.list_vocab, self.items_vocab):
            for term in v:
                self.assert_(v.get_term(term.value) is term)
                self.assert_(v.get_term_bytoken(term.token) is term)

    def test_getitem(self):
        t = self.list_vocab[0]
        self.assertIs(t, self.list_vocab.get_term(1))

    def test_getvalue(self):
        self.assertEqual(self.items_vocab.get_value('one'), 1)
        self.assertRaises(LookupError, self.items_vocab.get_value, 'unknown')

    def test_getterm(self):
        term = self.items_vocab.get_term(1)
        self.assertEqual(term.token, 'one')
        self.assertRaises(LookupError, self.items_vocab.get_term, 500)

    def test_getterm_bytoken(self):
        term = self.items_vocab.get_term_bytoken('one')
        self.assertEqual(term.token, 'one')
        self.assertEqual(term.value, 1)
        self.assertRaises(LookupError,
                          self.items_vocab.get_term_bytoken, 'unknown')

    def test_nonunique_tokens(self):
        self.assertRaises(
            ValueError, vocabulary.Vocabulary, 2, '2')
        self.assertRaises(
            ValueError, vocabulary.Vocabulary,
            ('one', 1, 'one'), ('another one', '1', 'another one'))
        self.assertRaises(
            ValueError, vocabulary.Vocabulary,
            ('one', 0), ('one', 1))

    def test_nonunique_token_message(self):
        try:
            vocabulary.Vocabulary(2, '2')
        except ValueError as e:
            self.assertEquals(str(e), "term tokens must be unique: '2'")

    def test_nonunique_token_messages(self):
        try:
            vocabulary.Vocabulary(('one', 0), ('one', 1))
        except ValueError as e:
            self.assertEquals(str(e), "term values must be unique: 'one'")

    def test_overriding_create_term(self):
        class MyTerm(object):
            def __init__(self, value):
                self.value = value
                self.token = repr(value)
                self.nextvalue = value + 1

        class MyVocabulary(vocabulary.Vocabulary):
            @classmethod
            def create_term(cls, value):
                return MyTerm(value)

        vocab = MyVocabulary(1, 2, 3)
        for term in vocab:
            self.assertEqual(term.value + 1, term.nextvalue)
