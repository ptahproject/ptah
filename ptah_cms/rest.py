""" rest api for cms """
from zope import interface
from zope.interface import providedBy
from memphis import config, form
from collections import OrderedDict

import ptah
import ptah_cms
from ptah_cms.node import load
from ptah_cms.content import Content
from ptah_cms.container import Container

from cms import cms
from interfaces import Error, NotFound, CmsException
from interfaces import INode, IBlob, IContent, IContainer
from permissions import View, ModifyContent, DeleteContent


CMS = ptah.restService('cms', 'Ptah CMS API')


@CMS.action('applications', 'List applications')
def cmsApplications(request, *args):
    apps = []

    for name, factory in ptah_cms.Factories.items():
        root = factory(request)

        try:
            info = cms(root).info()
        except (AttributeError, CmsException):
            continue

        info['__mount__'] = name
        info['__link__'] = '%s/content:%s/%s/'%(
            request.application_url, name, root.__uri__)
        apps.append(info)

    return apps


@CMS.action('types', 'List content types')
def cmsTypes(request, *args):
    types = []

    for name, tinfo in ptah_cms.Types.items():
        types.append((tinfo.title, name, typeInfo(tinfo, request)))

    types.sort()
    return [info for _t, name, info in types]


def typeInfo(tinfo, request):
    info = OrderedDict(
        (('__uri__', tinfo.__uri__),
         ('name', tinfo.name),
         ('title', tinfo.title),
         ('description', tinfo.description),
         ('permission', tinfo.permission),
         ('fieldset', []),
         ))

    fieldset = info['fieldset']

    for field in tinfo.fieldset.fields():
        fieldset.append(
            OrderedDict(
                (('type', field.__field__),
                 ('name', field.name),
                 ('title', field.title),
                 ('description', field.description),
                 ('required', field.required),
                 )))

    return info


@CMS.action('content', 'CMS content')
def cmsContent(request, app, uri=None, action='', *args):
    info = {}

    appfactory = ptah_cms.Factories.get(app)
    if appfactory is None:
        raise NotFound()

    root = appfactory(request)
    request.root = root

    if not uri:
        content = root
    else:
        content = load(uri)

    adapters = config.registry.adapters

    action = adapters.lookup(
        (IRestActionClassifier, providedBy(content)),
        IRestAction, name=action, default=None)

    if action:
        request.environ['SCRIPT_NAME'] = '%s/content:%s/'%(
            request.environ['SCRIPT_NAME'], app)

        ptah.checkPermission(action.permission, content, request)
        res = action.callable(content, request, *args)
        if not res: # pragma: no cover
            res = {}
        return res

    raise NotFound()


class IRestAction(interface.Interface):
    pass


class IRestActionClassifier(interface.Interface):
    pass


class Action(object):
    interface.implements(IRestAction)

    def __init__(self, callable, name, permission):
        self.callable = callable
        self.name = name
        self.title = name
        self.description = callable.__doc__
        self.permission = permission


def restAction(name, context, permission):
    info = config.DirectiveInfo()

    def _register(callable, name, context, permission):
        ac = Action(callable, name, permission)
        config.registry.registerAdapter(
            ac, (IRestActionClassifier, context), IRestAction, name)

    def wrapper(func):
        info.attach(
            config.Action(
                _register,
                (func, name, context, permission),
                discriminator = ('ptah_cms:rest-action', name, context))
            )
        return func

    return wrapper


@restAction('', IContent, View)
def nodeInfo(content, request, *args):
    info = cms(content).info()
    info['__link__'] = '%s%s/'%(request.application_url, content.__uri__)
    return info


@restAction('', IContainer, View)
def containerNodeInfo(content, request, *args):
    """Container information"""
    info = nodeInfo(content, request)

    contents = []
    for item in content.values():
        if not ptah.checkPermission(
            View, item, request, False): # pragma: no cover
            continue

        contents.append(
            OrderedDict((
                    ('__name__', item.__name__),
                    ('__type__', item.__type_id__),
                    ('__uri__', item.__uri__),
                    ('__container__', isinstance(item, Container)),
                    ('__link__', '%s%s/'%(request.application_url,
                                          item.__uri__)),
                    ('title', item.title),
                    ('description', item.description),
                    ('created', item.created),
                    ('modified', item.modified),
                    )))

    info['__contents__'] = contents
    return info


@restAction('apidoc', INode, View)
def apidocAction(content, request, *args):
    """api doc"""
    actions = []
    url = request.application_url
    for name, action in config.registry.adapters.lookupAll(
        (IRestActionClassifier, providedBy(content)), IRestAction):

        if not ptah.checkPermission(
            action.permission, content, request, False):
            continue

        actions.append(
            (name, action.title,
             OrderedDict(
                    (('name', name or 'info'),
                     ('link', '%s%s/%s'%(url, content.__uri__, name)),
                     ('title', action.title),
                     ('description', action.description)))))

    actions.sort()
    return [action for _t, _n, action in actions]


@restAction('delete', IContent, DeleteContent)
def deleteAction(content, request, *args):
    """Delete content"""
    content.delete()


@restAction('move', IContent, ModifyContent)
def moveAction(content, request, *args):
    """Move content"""


@restAction('update', IContent, ModifyContent)
def updateAction(content, request, *args):
    """Update content"""
    tinfo = content.__type__

    fieldset = tinfo.fieldset.bind(None, request.POST)
    data, errors = fieldset.extract()
    if errors:
        request.response.status = 500
        return {'errors': errors.msg}

    content.update(**data)
    return nodeInfo(content, request)


@restAction('create', IContainer, View)
def createContentAction(content, request, *args):
    """Create content"""
    name = request.GET.get('name')
    tinfo = request.GET.get('tinfo')

    tinfo = ptah.resolve(tinfo)

    fieldset = tinfo.fieldset.bind(None, request.POST)
    data, errors = fieldset.extract()
    if errors:
        request.response.status = 500
        return {'errors': errors.msg}

    item = cms(content).create(tinfo.__uri__, name, **data)
    return nodeInfo(item, request)


@restAction('data', IBlob, View)
def blobData(content, request, *args):
    """Download blob"""
    response = request.response

    info = content.info()
    response.content_type = info['mimetype'].encode('utf-8')
    if info['filename']:
        response.headerlist = {
            'Content-Disposition':
            'filename="%s"'%info['filename'].encode('utf-8')}
    response.body = content.read()
    return response
