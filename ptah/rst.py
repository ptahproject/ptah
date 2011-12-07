import os.path
import logging
import tempfile
import threading
import pkg_resources
from docutils import io
from docutils.core import Publisher
from pyramid.compat import text_type, bytes_

from sphinx.application import Sphinx
from sphinx.writers.html import HTMLWriter, HTMLTranslator

log = logging.getLogger('ptah.rst')
local_data = threading.local()

tempdir = tempfile.mkdtemp()
tmp = open(os.path.join(tempdir, 'conf.py'), 'wb')
tmp.write(bytes_('# -*- coding: utf-8 -*-'))
tmp.close()


def get_sphinx():
    sphinx = getattr(local_data, 'sphinx', None)
    if sphinx is None:
        sphinx = Sphinx(tempdir, tempdir, tempdir,
                        tempdir, 'json', status=None, warning=None)
        sphinx.builder.translator_class = CustomHTMLTranslator

        sphinx.env.patch_lookup_functions()
        sphinx.env.temp_data['docname'] = 'text'
        sphinx.env.temp_data['default_domain'] = 'py'

        pub = Publisher(reader=None,
                        parser=None,
                        writer=HTMLWriter(sphinx.builder),
                        source_class=io.StringInput,
                        destination_class=io.NullOutput)
        pub.set_components('standalone', 'restructuredtext', None)
        pub.process_programmatic_settings(None, sphinx.env.settings, None)
        pub.set_destination(None, None)

        sphinx.publisher = pub

        local_data.sphinx = sphinx

    return sphinx, sphinx.publisher


def rst_to_html(text):
    if not isinstance(text, text_type):
        text = text_type(text)

    sphinx, pub = get_sphinx()

    pub.set_source(text, None)

    try:
        pub.publish()
    except:
        log.warning('ReST to HTML error\n %s', text)
        return '<pre>%s</pre>' % text

    doctree = pub.document
    sphinx.env.filter_messages(doctree)
    for domain in sphinx.env.domains.values():
        domain.process_doc(sphinx.env, 'text', doctree)

    pub.writer.write(doctree, io.StringOutput(encoding='unicode'))
    pub.writer.assemble_parts()

    parts = pub.writer.parts
    return ''.join((parts['body_pre_docinfo'],
                    parts['docinfo'], parts['body']))


class CustomHTMLTranslator(HTMLTranslator):

    def visit_pending_xref(self, node):
        pass

    def depart_pending_xref(self, node):
        pass
