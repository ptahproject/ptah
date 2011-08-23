""" introspect module """
import ptah
from memphis import config
from zope import interface
from interfaces import IIntrospectModule, ITemplatesModule


class IntrospectModule(ptah.PtahModule):
    config.utility(name='introspect')
    interface.implementsOnly(IIntrospectModule)

    name = 'introspect'
    title = 'Introspect'
    description = 'Memphis introspection of various aspects.'
