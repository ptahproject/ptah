""" pyramid/zope compatibility """
from zope import interface
from zope.i18n.locales import locales
from zope.i18n.interfaces import IUserPreferredLanguages

try:
    from zope.i18n import translate as i18n_translate
    from zope.publisher.interfaces.browser \
        import IBrowserView as IZopeView
    from zope.publisher.interfaces.browser \
        import IBrowserRequest as IZopeRequest
except ImportError:
    class IZopeView(interface.Interface):
        pass
    class IZopeRequest(interface.Interface):
        pass

try:
    from pyramid.i18n import TranslationStringFactory
except ImportError:
    from zope.i18nmessageid import MessageFactory as TranslationStringFactory

try:
    from pyramid.i18n import get_locale_name, get_localizer
    from pyramid.interfaces import IView as IPyramidView
    from pyramid.interfaces import IRequest as IPyramidRequest
except:
    class IPyramidView(interface.Interface):
        pass
    class IPyramidRequest(interface.Interface):
        pass


from interfaces import IView


class IView(IView, IZopeView, IPyramidView):
    """ view """


def getLocale(request):
    if IPyramidRequest.providedBy(request):
        return locales.getLocale(get_locale_name(request), None, None)

    if hasattr(request, 'locale'):
        return request.locale

    if not getattr(request, '_processed', False):
        envadapter = IUserPreferredLanguages(request, None)
        if envadapter is not None:
            langs = envadapter.getPreferredLanguages()
            for httplang in langs:
                parts = (httplang.split('-') + [None, None])[:3]
                try:
                    locale = locales.getLocale(*parts)
                except LoadLocaleError:
                    pass
            else:
                locale = locales.getLocale(None, None, None)

            request.locale = locale
            return locale


def translate(msgid, context=None, domain=None, mapping=None, 
              target_language=None, default=None):
    if IPyramidRequest.providedBy(context):
        return get_localizer(context).translate(msgid, domain, mapping)
    else:
        return i18n_translate(msgid, domain=domain, mapping=mapping,
                              context=context, target_language=target_language,
                              default=default)
