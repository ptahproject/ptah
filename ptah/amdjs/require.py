""" amdjs init for request """
import logging
from collections import namedtuple
from ptah.amdjs.amd import ID_AMD_SPEC, ID_AMD_BUILD_MD5

log = logging.getLogger('ptah.amdjs')

amdjs_data = namedtuple('amdjs_data', 'js css spec init')


def amdjs_tween_factory(handler, registry):
    settings = registry.settings

    enabled = settings['amd.enabled']
    build_md5 = registry[ID_AMD_BUILD_MD5]
    specstorage = registry[ID_AMD_SPEC]

    def amdjs_tween(request):
        """ amdjs tween without spec support """
        if ('text/html' not in request.accept or request.is_xhr):
            return handler(request)

        response = handler(request)

        if ('amdjs_data' in request.__dict__ and
                request.amdjs_data['init'] and
                response.content_type == 'text/html' and
                response.status_code == 200 and
                response.content_length != 0 and
                response.headers.get('Transfer-Encoding', '') != 'chunked'):

            data = request.amdjs_data
            response._amdjs_inititalized = True

            spec = data['spec']
            if enabled and spec not in ('', '_'):
                specdata = specstorage.get(spec)
                if not specdata:
                    log.warn("Spec '%s' is not found.", spec)
                    spec = '_'

            if enabled and spec not in ('', '_'):
                initfile = '%s-init' % spec
                c_tmpls = [
                    '\n<script src="%s"> </script>' % (
                        request.static_url(
                            specstorage[initfile],
                            _query={'_v': build_md5(request, spec)}))]
            else:
                c_tmpls = [
                    '\n<script src="%s"> </script>' % (
                        request.route_url(
                            'pyramid-amd-init', specname='_',
                            _query={'_v': build_md5(request, '_')}))]

            mods = ["'%s'" % m for m in data['js']]
            mods.extend("'css!%s'" % c for c in data['css'])

            if mods:
                c_tmpls.append(
                    ('<script type="text/javascript">'
                     'curl({paths:pyramid_amd_modules},[%s])</script>' %
                     ','.join(mods)))

            if data['fn']:
                c_tmpls.append(
                    '<script type="text/javascript">\n%s</script>' %
                    ';\n'.join(data['fn']))

            text = response.text
            pos = text.find('</head>')
            if pos:
                response.text = '%s%s\n%s' % (
                    text[:pos], '\n'.join(c_tmpls), text[pos:])

        return response

    return amdjs_tween


def require_js(request, *mods):
    request.amdjs_data['init'] = True

    js = request.amdjs_data['js']
    for mod in mods:
        if mod not in js:
            js.append(mod)


def require_css(request, *mods):
    request.amdjs_data['init'] = True

    css = request.amdjs_data['css']
    for mod in mods:
        if mod not in css:
            css.append(mod)


def require_fn(request, require, fn):
    request.amdjs_data['init'] = True

    request.amdjs_data['fn'].append(
        'curl([%s], %s)' % (','.join("'%s'" % s for s in require), fn))


def require_spec(request, spec):
    request.amdjs_data['init'] = True

    if request.amdjs_data['spec']:
        log.warn("ptah.amdjs spec is already set: %s, %s",
                 request.amdjs_data['spec'], spec)
    else:
        request.amdjs_data['spec'] = spec
