""" rest api for cms """
import ptah
import sqlalchemy as sqla
from collections import OrderedDict
from zope import interface
from zope.interface import providedBy
from zope.component import getSiteManager
from memphis import config
from pyramid.location import lineage
from pyramid.httpexceptions import HTTPNotFound

from ptah_cms.node import Node
from ptah_cms.content import Content
from ptah_cms.container import Container
from ptah_cms.root import factories
from ptah_cms.interfaces import IContent
from ptah_cms.interfaces import IContainer
from ptah_cms.interfaces import IRestAction
from ptah_cms.interfaces import IRestActionClassifier
from ptah_cms.interfaces import ContentSchema

from ptah_cms.container import loadContent


class Applications(ptah.rest.Action):

    name = 'applications'
    title = 'List applications'
    
    def __call__(self, request, *args):
        apps = []

        for name, factory in factories.items():
            root = factory(request)
            
            apps.append((root.title, root.name, {
                '__name__': root.name,
                '__uuid__': root.__uuid__,
                '__link__': '%s/content:%s/%s/'%(
                    request.application_url, root.name, root.__uuid__),
                }))

        apps.sort()
        return OrderedDict((name, info) for _t, name, info in apps)


class Content(ptah.rest.Action):

    name = 'content'
    title = 'CMS Content'

    def __call__(self, request, app, uuid=None, action='', *args):
        info = {}

        appfactory = factories.get(app)
        if appfactory is None:
            raise HTTPNotFound

        root = appfactory(request)
        request.root = root

        if not uuid:
            content = root
        else:
            content = loadContent(uuid, ptah.View)

        adapters = request.registry.adapters

        actionFactory = adapters.lookup(
            (IRestActionClassifier, providedBy(content)),
            IRestAction, name=action, default=None)

        if actionFactory:
            request.environ['SCRIPT_NAME'] = '%s/content:%s/'%(
                request.environ['SCRIPT_NAME'], app)

            return actionFactory(content, request)

        raise HTTPNotFound()


def registerRestAction(name, context, factory):
    info = config.DirectiveInfo()

    info.attach(
        config.Action(
            registerRestActionImpl,
            (name, context, factory),
            discriminator = ('ptah_cms:rest-action', name, context))
        )


def registerRestActionImpl(name, context, factory):
    getSiteManager().registerAdapter(
        factory, (IRestActionClassifier, context), IRestAction, name)


class ContentRestInfo(object):
    interface.implements(IRestAction)

    title = 'Content information'
    description = ''

    def parents(self, content):
        parents = []

        for item in lineage(content):
            if isinstance(item, Node):
                parents.append(item.__uuid__)
            else:
                break

        return parents

    def __call__(self, content, request):
        info = OrderedDict(
            (('__name__', content.name),
             ('__path__', content.__path__),
             ('__type__', content.__type_id__),
             ('__uuid__', content.__uuid__),
             ('__container__', False),
             ('__link__', '%s%s/'%(request.application_url, content.__uuid__)),
             ('__parents__', self.parents(content)),
             ))

        schema = content.__type__.schema
        if schema is None:
            schema = ContentSchema
        
        for node in schema:
            val = getattr(content, node.name, node.missing)
            info[node.name] = node.serialize(val)

        info['view'] = content.view
        info['created'] = content.created
        info['modified'] = content.modified
        info['effective'] = content.effective
        info['expires'] = content.expires

        return info


class ContainerRestInfo(ContentRestInfo):

    title = 'Container information'
    description = ''

    def __call__(self, content, request):
        info = super(ContainerRestInfo, self).__call__(content, request)
        
        contents = []
        for content in content.__children__:
            contents.append(
                OrderedDict((
                    ('__name__', content.name),
                    ('__path__', content.__path__),
                    ('__type__', content.__type_id__),
                    ('__uuid__', content.__uuid__),
                    ('__container__', isinstance(content, Container)),
                    ('__link__', '%s%s/'%(request.application_url,
                                          content.__uuid__)),
                    ('title', content.title),
                    ('description', content.description))))

        info['__contents__'] = contents
        info['__container__'] = True
        return info


class ContentAPIDoc(ContentRestInfo):

    title = 'API Doc'
    description = ''

    def __call__(self, content, request):
        info = super(ContentAPIDoc, self).__call__(content, request)

        info['__actions__'] = []
        
        url = request.application_url
        for name, actionFactory in request.registry.adapters.lookupAll(
            (IRestActionClassifier, providedBy(content)), IRestAction):

            info['__actions__'].append(
                OrderedDict(
                    (('name', name),
                     ('link', '%s%s/%s'%(url, content.__uuid__, name)), 
                     ('title', actionFactory.title),
                     ('description', actionFactory.description))))

        return info


registerRestAction('', IContent, ContentRestInfo())
registerRestAction('', IContainer, ContainerRestInfo())
registerRestAction('apidoc', IContent, ContentAPIDoc())

ptah.rest.registerService('cms', 'cms', 'Ptah CMS api')
ptah.rest.registerServiceAction('cms', Content())
ptah.rest.registerServiceAction('cms', Applications())
