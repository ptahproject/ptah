from zope.interface import implementer
from pyramid.compat import string_types
from ptah.form.interfaces import ITerm, IVocabulary


@implementer(ITerm)
class Term(object):
    """Simple tokenized term used by Vocabulary."""

    def __init__(self, value, token=None,
                 title=None, description=None, **kw):
        """Create a term for value and token. If token is omitted,
        str(value) is used for the token.
        """
        self.__dict__.update(kw)

        self.value = value
        if token is None:
            token = value
        if title is None:
            title = str(value)
        self.token = str(token)
        self.title = title
        self.description = description

    def __str__(self):
        return 'Term<"%s:%s:%s">'%(self.value, self.token, self.title)

    __repr__ = __str__


@implementer(IVocabulary)
class Vocabulary(object):
    """Vocabulary that works from a sequence of terms."""

    def __init__(self, *items):
        """Initialize the vocabulary given a list of terms.

        The vocabulary keeps a reference to the list of terms passed
        in; it should never be modified while the vocabulary is used.

        Also it is possible to initialize vocabulary with sequence of items,
        in this case constructor automatically creates `Term` objects.
        """
        terms = []
        for rec in items:
            if ITerm.providedBy(rec):
                terms.append(rec)
                continue
            if isinstance(rec, string_types):
                rec = (rec,)
            if not hasattr(rec, '__iter__'):
                rec = (rec,)
            if len(rec) == 2:
                terms.append(self.create_term(rec[0], rec[1], rec[1]))
            else:
                terms.append(self.create_term(*rec))

        self.by_value = {}
        self.by_token = {}
        self._terms = terms
        for term in self._terms:
            if term.value in self.by_value:
                raise ValueError(
                    'term values must be unique: %s' % repr(term.value))
            if term.token in self.by_token:
                raise ValueError(
                    'term tokens must be unique: %s' % repr(term.token))
            self.by_value[term.value] = term
            self.by_token[term.token] = term

    @classmethod
    def create_term(cls, *args):
        """Create a single term from data."""
        return Term(*args)

    def __contains__(self, value):
        try:
            return value in self.by_value
        except:
            # sometimes values are not hashable
            return False

    def get_term(self, value):
        try:
            return self.by_value[value]
        except:
            raise LookupError(value)

    def get_term_bytoken(self, token):
        try:
            return self.by_token[token]
        except:
            raise LookupError(token)

    def get_value(self, token):
        return self.get_term_bytoken(token).value

    def __iter__(self):
        return iter(self._terms)

    def __len__(self):
        return len(self.by_value)

    def __getitem__(self, index):
        return self._terms[index]
