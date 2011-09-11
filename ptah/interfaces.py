""" interfaces """
import translationstring
from memphis import view
from zope import interface

_ = translationstring.TranslationStringFactory('ptah')


class IPtahRoute(interface.Interface):
    """ ptah route """


class IPtahManageRoute(view.INavigationRoot):
    """ user management route """


class IPtahModule(interface.Interface):
    """ module """

    name = interface.Attribute('Module name')
    title = interface.Attribute('Module title')

    def url(request):
        """ return url to this module """

    def bind(manager, request):
        """ bind module to context """

    def available(request):
        """ is module available """
