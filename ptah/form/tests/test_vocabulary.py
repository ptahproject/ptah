##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Test of the Vocabulary and related support APIs.
"""
from ptah.form import vocabulary
from ptah.testing import TestCase


class SimpleVocabularyTests(TestCase):

    list_vocab = vocabulary.SimpleVocabulary.from_values(1, 2, 3)
    items_vocab = vocabulary.SimpleVocabulary.from_items(
        (1, 'one'), (2, 'two'), (3, 'three'), (4, 'fore!'))

    def test_simple_term(self):
        t = vocabulary.SimpleTerm(1)
        self.assertEqual(t.value, 1)
        self.assertEqual(t.token, "1")
        t = vocabulary.SimpleTerm(1, "One")
        self.assertEqual(t.value, 1)
        self.assertEqual(t.token, "One")

    def test_simple_term_title(self):
        t = vocabulary.SimpleTerm(1)
        self.assertIsNone(t.title)
        t = vocabulary.SimpleTerm(1, title="Title")
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
            ValueError, vocabulary.SimpleVocabulary.from_values, 2, '2')
        self.assertRaises(
            ValueError, vocabulary.SimpleVocabulary.from_items,
            ('one', 1), ('another one', '1'))
        self.assertRaises(
            ValueError, vocabulary.SimpleVocabulary.from_items,
            ('one', 0), ('one', 1))

    def test_nonunique_token_message(self):
        try:
            vocabulary.SimpleVocabulary.from_values(2, '2')
        except ValueError as e:
            self.assertEquals(str(e), "term tokens must be unique: '2'")

    def test_nonunique_token_messages(self):
        try:
            vocabulary.SimpleVocabulary.from_items(('one', 0), ('one', 1))
        except ValueError as e:
            self.assertEquals(str(e), "term values must be unique: 'one'")

    def test_overriding_create_term(self):
        class MyTerm(object):
            def __init__(self, value):
                self.value = value
                self.token = repr(value)
                self.nextvalue = value + 1

        class MyVocabulary(vocabulary.SimpleVocabulary):
            def create_term(cls, value):
                return MyTerm(value)
            create_term = classmethod(create_term)

        vocab = MyVocabulary.from_values(1, 2, 3)
        for term in vocab:
            self.assertEqual(term.value + 1, term.nextvalue)
