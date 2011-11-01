import docutils.core


def rest_to_html(text):
    if not isinstance(text, unicode):
        text = unicode(text, 'utf-8')
    
    overrides = {
        'halt_level': 6,
        'input_encoding': 'unicode',
        'output_encoding': 'unicode',
        'initial_header_level': 3,
        }
    parts = docutils.core.publish_parts(
        text,
        writer_name='html',
        settings_overrides=overrides,
        )
    return u''.join((parts['body_pre_docinfo'],
                     parts['docinfo'], parts['body']))
