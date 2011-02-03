import doctest as pythondoctest

import lxml.etree
import lxml.doctestcompare

import re


class OutputChecker(lxml.doctestcompare.LHTMLOutputChecker):
    """Doctest output checker which is better equippied to identify
    HTML markup than the checker from the ``lxml.doctestcompare``
    module. It also uses the text comparison function from the
    built-in ``doctest`` module to allow the use of ellipsis."""

    _repr_re = re.compile(
        r'^<([A-Z]|[^>]+ (at|object) |[a-z]+ \'[A-Za-z0-9_.]+\'>)')

    def __init__(self, doctest=pythondoctest):
        self.doctest = doctest

        # make sure these optionflags are registered
        doctest.register_optionflag('PARSE_HTML')
        doctest.register_optionflag('PARSE_XML')
        doctest.register_optionflag('NOPARSE_MARKUP')

    def _looks_like_markup(self, s):
        s = s.replace('<BLANKLINE>', '\n').strip()
        return (s.startswith('<')
                and not self._repr_re.search(s))

    def text_compare(self, want, got, strip):
        if want is None:
            want = ""
        if got is None:
            got = ""
        checker = self.doctest.OutputChecker()
        return checker.check_output(
            want, got, self.doctest.ELLIPSIS|self.doctest.NORMALIZE_WHITESPACE)

    def get_parser(self, want, got, optionflags):
        NOPARSE_MARKUP = self.doctest.OPTIONFLAGS_BY_NAME.get(
            "NOPARSE_MARKUP", 0)
        PARSE_HTML = self.doctest.OPTIONFLAGS_BY_NAME.get(
            "PARSE_HTML", 0)
        PARSE_XML = self.doctest.OPTIONFLAGS_BY_NAME.get(
            "PARSE_XML", 0)

        parser = None
        if NOPARSE_MARKUP & optionflags:
            return None
        if PARSE_HTML & optionflags:
            parser = lxml.doctestcompare.html_fromstring
        elif PARSE_XML & optionflags:
            parser = lxml.etree.XML
        elif (want.strip().lower().startswith('<html')
              and got.strip().startswith('<html')):
            parser = lxml.doctestcompare.html_fromstring
        elif (self._looks_like_markup(want)
              and self._looks_like_markup(got)):
            parser = self.get_default_parser()
        return parser
