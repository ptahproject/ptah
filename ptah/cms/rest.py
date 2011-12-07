""" rest api for cms """
from collections import OrderedDict
from zope.interface import providedBy, implementer, Interface
from pyramid.compat import bytes_

import ptah
from ptah import config
from ptah.cms import wrap
from ptah.cms.node import load
from ptah.cms.container import Container
from ptah.cms.interfaces import NotFound, CmsException
from ptah.cms.interfaces import INode, IBlob, IContent, IContainer
from ptah.cms.permissions import View, ModifyContent, DeleteContent

ID_CMS_REST = 'ptah-cms:rest-action'
CMS = ptah.RestService('cms', 'Ptah CMS API')


@CMS.action('applications', 'List applications')
def cmsApplications(request, *args):
    apps = []

    for name, factory in ptah.cms.get_app_factories().items():
        root = factory(request)

        try:
            info = wrap(root).info()
        except (AttributeError, CmsException):
            continue

        info['__mount__'] = name
        if name:
            info['__link__'] = '%s/content:%s/%s/'%(
                request.application_url, name, root.__uri__)
        else:
            info['__link__'] = '%s/content/%s/'%(
                request.application_url, root.__uri__)
        apps.append(info)

    return apps


@CMS.action('types', 'List content types')
def cmsTypes(request, *args):
    types = []

    for name, tinfo in ptah.cms.get_types().items():
        types.append((tinfo.title, name, typeInfo(tinfo, request)))

    return [info for _t, name, info in sorted(types)]


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
def cmsContent(request, app='', uri=None, action='', *args):
    name = getattr(request, 'subpath', ('content',))[0]
    if ':' not in name:
        if not action:
            action = uri or ''
        uri = app
        app = ''

    content = None

    appfactory = ptah.cms.get_app_factories().get(app)
    if appfactory is not None:
        root = appfactory(request)
        request.root = root

        if not uri:
            content = root

    if content is None:
        content = load(uri)

    adapters = request.registry.adapters

    action = adapters.lookup(
        (IRestActionClassifier, providedBy(content)),
        IRestAction, name=action, default=None)

    if action:
        if app:
            request.environ['SCRIPT_NAME'] = '%s/content:%s/'%(
                request.environ['SCRIPT_NAME'], app)
        else:
            request.environ['SCRIPT_NAME'] = '%s/content/'%(
                request.environ['SCRIPT_NAME'])

        ptah.check_permission(action.permission, content, request, True)
        res = action.callable(content, request, *args)
        if not res: # pragma: no cover
            res = {}
        return res

    raise NotFound()


class IRestAction(Interface):
    pass


class IRestActionClassifier(Interface):
    pass


@implementer(IRestAction)
class Action(object):
    """ Rest action """

    def __init__(self, callable, name, permission):
        self.callable = callable
        self.name = name
        self.title = name
        self.description = callable.__doc__
        self.permission = permission


def restaction(name, context, permission):
    info = config.DirectiveInfo()

    def wrapper(func):
        discr = (ID_CMS_REST, name, context)
        intr = config.Introspectable(ID_CMS_REST, discr, name, ID_CMS_REST)
        intr['name'] = name
        intr['context'] = context
        intr['permission'] = permission
        intr['callable'] = func

        def _register(cfg, callable, name, context, permission):
            ac = Action(callable, name, permission)
            cfg.registry.registerAdapter(
                ac, (IRestActionClassifier, context), IRestAction, name)

        info.attach(
            config.Action(
                _register,
                (func, name, context, permission),
                discriminator=discr, introspectables=(intr,))
            )
        return func

    return wrapper


@restaction('', INode, View)
def nodeInfo(content, request, *args):
    info = wrap(content).info()
    info['__link__'] = '%s%s/'%(request.application_url, content.__uri__)
    return info


@restaction('', IContainer, View)
def containerNodeInfo(content, request, *args):
    """Container information"""
    info = nodeInfo(content, request)

    contents = []
    for item in content.values():
        if not ptah.check_permission(View, item, request): # pragma: no cover
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


@restaction('apidoc', INode, ptah.NO_PERMISSION_REQUIRED)
def apidocAction(content, request, *args):
    """api doc"""
    actions = []
    url = request.application_url
    for name, action in request.registry.adapters.lookupAll(
        (IRestActionClassifier, providedBy(content)), IRestAction):

        if not ptah.check_permission(
            action.permission, content, request):
            continue

        actions.append(
            (name, action.title,
             OrderedDict(
                    (('name', name or 'info'),
                     ('link', '%s%s/%s'%(url, content.__uri__, name)),
                     ('title', action.title),
                     ('description', action.description)))))

    return [action for _t, _n, action in sorted(actions)]


@restaction('delete', IContent, DeleteContent)
def deleteAction(content, request, *args):
    """Delete content"""
    content.delete()


@restaction('move', IContent, ModifyContent)
def moveAction(content, request, *args):
    """Move content"""


@restaction('update', IContent, ModifyContent)
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


@restaction('create', IContainer, View)
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

    item = wrap(content).create(tinfo.__uri__, name, **data)
    return nodeInfo(item, request)


@restaction('data', IBlob, View)
def blobData(content, request, *args):
    """Download blob"""
    response = request.response

    info = content.info()
    response.content_type = info['mimetype']
    if info['filename']:
        response.headerlist = {
            'Content-Disposition':
            bytes_('filename="{0}"'.format(info['filename']), 'utf-8')}
    response.body = content.read()
    return response
