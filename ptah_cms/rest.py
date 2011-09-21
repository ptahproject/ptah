""" rest api for cms """
import colander
from collections import OrderedDict
from zope import interface
from zope.interface import providedBy
from zope.component import getSiteManager
from memphis import config, form
from pyramid.location import lineage
from pyramid.httpexceptions import HTTPNotFound

import ptah
import ptah_cms
from ptah_cms.node import Node
from ptah_cms.content import Content
from ptah_cms.content import loadContent
from ptah_cms.container import Container
from ptah_cms.root import factories
from ptah_cms.interfaces import IContent
from ptah_cms.interfaces import IContainer
from ptah_cms.interfaces import IRestAction
from ptah_cms.interfaces import IRestActionClassifier


class Applications(ptah.rest.Action):

    name = 'applications'
    title = 'List applications'
    
    def __call__(self, request, *args):
        apps = []

        for name, factory in factories.items():
            root = factory(request)

            apps.append((root.title, root.__name__, OrderedDict(
                (('mount', name),
                 ('__name__', root.__name__),
                 ('__uuid__', root.__uuid__),
                 ('__link__', '%s/content:%s/%s/'%(
                     request.application_url, name, root.__uuid__))),
                )))

        apps.sort()
        return [info for _t, name, info in apps]


class Types(ptah.rest.Action):

    name = 'types'
    title = 'List content types'

    def __call__(self, request, *args):
        apps = []

        for name, tinfo in ptah_cms.registeredTypes.items():

            apps.append((tinfo.title, name, OrderedDict(
                (('name', name),
                 ('title', tinfo.title),
                 ('description', tinfo.description),
                 ('__link__', '%s/type:%s/'%(
                     request.application_url, name))),
                )))

        apps.sort()
        return [info for _t, name, info in apps]


class Type(ptah.rest.Action):

    name = 'type'
    title = 'CMS Content Type'

    def __call__(self, request, tname, actionId='', *args):
        info = {}

        tinfo = ptah_cms.registeredTypes.get(tname)
        if tinfo is None:
            raise HTTPNotFound

        action = None
        if not actionId:
            action = TypeRestInfo()

        if action:
            request.environ['SCRIPT_NAME'] = '%s/type:%s/'%(
                request.environ['SCRIPT_NAME'], tname)

            res = action(tinfo, request, *args)
            if not res:
                res = {'success': True}
            return res

        raise HTTPNotFound()


class TypeRestInfo(object):

    title = 'Type information'
    description = ''

    def __call__(self, tinfo, request, *args):
        info = OrderedDict(
            (('name', tinfo.name),
             ('title', tinfo.title),
             ('description', tinfo.description),
             ('permission', tinfo.permission),
             ('schema', []),
             ))

        schema = info['schema']

        for node in tinfo.schema.children \
                + ptah_cms.ContentNameSchema().children:
            widget = node.widget
            if not widget:
                widget = form.getDefaultWidgetName(node)
                
            schema.append(
                OrderedDict(
                    (('name', node.name),
                     ('title', node.title),
                     ('description', node.description),
                     ('required', node.required),
                     ('widget', widget),
                     )))

        return info


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
            content = loadContent(uuid)

        adapters = request.registry.adapters

        action = adapters.lookup(
            (IRestActionClassifier, providedBy(content)),
            IRestAction, name=action, default=None)

        if action:
            request.environ['SCRIPT_NAME'] = '%s/content:%s/'%(
                request.environ['SCRIPT_NAME'], app)

            ptah.security.checkPermission(content,action.__permission__,request)
            res = action(content, request, *args)
            if not res:
                res = {'success': True}
            return res

        raise HTTPNotFound()


def contentRestAction(name, context, factory):
    info = config.DirectiveInfo()

    info.attach(
        config.Action(
            contentRestActionImpl,
            (name, context, factory),
            discriminator = ('ptah_cms:rest-action', name, context))
        )


def contentRestActionImpl(name, context, factory):
    getSiteManager().registerAdapter(
        factory, (IRestActionClassifier, context), IRestAction, name)


class ContentRestInfo(object):
    interface.implements(IRestAction)

    title = 'Content information'
    description = ''

    __permission__ = ptah.View

    def parents(self, content):
        parents = []

        for item in lineage(content):
            if isinstance(item, Node):
                parents.append(item.__uuid__)
            else:
                break

        return parents[1:]

    def __call__(self, content, request, *args):
        info = OrderedDict(
            (('__name__', content.__name__),
             ('__type__', content.__type_id__),
             ('__uuid__', content.__uuid__),
             ('__container__', False),
             ('__link__', '%s%s/'%(request.application_url, content.__uuid__)),
             ('__parents__', self.parents(content)),
             ))

        schema = content.__type__.schema
        if schema is None:
            schema = ptah_cms.ContentSchema
        
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

    __permission__ = ptah.View

    def __call__(self, content, request, *args):
        info = super(ContainerRestInfo, self).__call__(content, request)
        
        contents = []
        for content in content.__children__:
            contents.append(
                OrderedDict((
                    ('__name__', content.__name__),
                    ('__type__', content.__type_id__),
                    ('__uuid__', content.__uuid__),
                    ('__container__', isinstance(content, Container)),
                    ('__link__', '%s%s/'%(request.application_url,
                                          content.__uuid__)),
                    ('title', content.title),
                    ('description', content.description),
                    ('created', content.created),
                    ('modified', content.modified),
                    )))

        info['__contents__'] = contents
        info['__container__'] = True
        return info


class ContentAPIDoc(ContentRestInfo):

    title = 'API Doc'
    description = ''

    __permission__ = ptah.View

    def __call__(self, content, request, *args):
        info = super(ContentAPIDoc, self).__call__(content, request)

        info['__actions__'] = []

        actions = []
        url = request.application_url
        for name, action in request.registry.adapters.lookupAll(
            (IRestActionClassifier, providedBy(content)), IRestAction):

            if not ptah.security.checkPermission(
                content, action.__permission__, request, False):
                continue

            actions.append(
                (name, action.title,
                 OrderedDict(
                     (('name', name),
                      ('link', '%s%s/%s'%(url, content.__uuid__, name)), 
                      ('title', action.title),
                      ('description', action.description)))))

        actions.sort()
        info['__actions__'] = [action for _t, _n, action in actions]

        return info


class DeleteAction(object):

    title = 'Delete content'
    description = ''

    __permission__ = ptah_cms.DeleteContent

    def __call__(self, content, request, *args):
        parent = content.__parent__
        if not isinstance(parent, Container):
            raise ptah.RestException("Can't remove content from non container")

        del parent[content]


class MoveAction(object):

    title = 'Move content'
    description = ''

    __permission__ = ptah_cms.ModifyContent

    def __call__(self, content, request, *args):
        pass


class UpdateAction(object):

    title = 'Update content'
    description = ''

    __permission__ = ptah_cms.ModifyContent

    def __call__(self, content, request, *args):
        tinfo = content.__type__

        try:
            data = tinfo.schema.deserialize(request.POST)
        except colander.Invalid, e:
            request.response.status = 500
            return {'errors': e.asdict()}

        for attr, value in data.items():
            setattr(content, attr, value)

        request.registry.notify(ptah_cms.events.ContentModifiedEvent(content))

        return ContentRestInfo()(content, request)


class CreateContentAction(object):

    title = 'Create content'
    description = ''

    __permission__ = ptah_cms.View

    name_schema = ptah_cms.ContentNameSchema()

    def __call__(self, content, request, uuid='', *args):
        if not isinstance(content, Container):
            raise ptah_cms.RestException(
                'Can create content only in container.')

        if not uuid:
            raise HTTPNotFound('Type information is not found')
        
        tinfo = ptah_cms.registeredTypes.get(uuid)
        if tinfo is None:
            raise HTTPNotFound('Type information is not found')

        ptah.security.checkPermission(content, tinfo.permission, request)

        try:
            data = tinfo.schema.deserialize(request.POST)
        except colander.Invalid, e:
            request.response.status = 500
            return {'errors': e.asdict()}

        try:
            name = self.name_schema.deserialize(request.POST)
            v = name['__name__']
            if v in content.keys():
                raise colander.Invalid(
                    self.name_schema['__name__'], 'Name already is in use')
        except colander.Invalid, e:
            request.response.status = 500
            return {'errors': e.asdict()}

        item = tinfo.create(**data)
        ptah_cms.Session.add(item)

        content[name['__name__']] = item

        return ContentRestInfo()(item, request)


contentRestAction('', IContent, ContentRestInfo())
contentRestAction('', IContainer, ContainerRestInfo())
contentRestAction('apidoc', IContent, ContentAPIDoc())
contentRestAction('create', IContent, CreateContentAction())
contentRestAction('update', IContent, UpdateAction())
contentRestAction('delete', IContent, DeleteAction())
contentRestAction('move', IContent, MoveAction())

ptah.registerService('cms', 'cms', 'Ptah CMS api')
ptah.registerServiceAction('cms', Content())
ptah.registerServiceAction('cms', Applications())
ptah.registerServiceAction('cms', Types())
ptah.registerServiceAction('cms', Type())
