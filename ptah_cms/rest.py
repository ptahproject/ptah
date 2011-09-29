""" rest api for cms """
import colander
from collections import OrderedDict
from zope import interface
from zope.interface import providedBy
from memphis import config, form
from pyramid.location import lineage
from pyramid.httpexceptions import HTTPNotFound

import ptah
import ptah_cms
from ptah_cms.node import Node
from ptah_cms.node import load
from ptah_cms.content import Content
from ptah_cms.container import Container
from ptah_cms.root import Factories
from ptah_cms.interfaces import IBlob
from ptah_cms.interfaces import IContent
from ptah_cms.interfaces import IContainer
from ptah_cms.interfaces import IRestAction
from ptah_cms.interfaces import IRestActionClassifier

from cms import cms
from interfaces import Error, CmsException
from permissions import View, ModifyContent, DeleteContent

from pprint import pprint


class Applications(ptah.rest.Action):

    name = 'applications'
    title = 'List applications'

    def __call__(self, request, *args):
        apps = []

        for name, factory in Factories.items():
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


class Types(ptah.rest.Action):

    name = 'types'
    title = 'List content types'

    def __call__(self, request, *args):
        types = []

        for name, tinfo in ptah_cms.Types.items():
            types.append((tinfo.title, name, self.typeInfo(tinfo, request)))

        types.sort()
        return [info for _t, name, info in types]

    def typeInfo(self, tinfo, request):
        info = OrderedDict(
            (('__uri__', tinfo.__uri__),
             ('name', tinfo.name),
             ('title', tinfo.title),
             ('description', tinfo.description),
             ('permission', tinfo.permission),
             ('schema', []),
             ))

        schema = info['schema']

        for node in tinfo.schema.children:
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

    def __call__(self, request, app, uri=None, action='', *args):
        info = {}

        appfactory = Factories.get(app)
        if appfactory is None:
            raise HTTPNotFound

        root = appfactory(request)
        request.root = root

        if not uri:
            content = root
        else:
            content = load(uri, policy=root.__parent__)

        adapters = request.registry.adapters

        action = adapters.lookup(
            (IRestActionClassifier, providedBy(content)),
            IRestAction, name=action, default=None)

        if action:
            request.environ['SCRIPT_NAME'] = '%s/content:%s/'%(
                request.environ['SCRIPT_NAME'], app)

            ptah.checkPermission(action.__permission__, content, request)
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
    config.registry.registerAdapter(
        factory, (IRestActionClassifier, context), IRestAction, name)


class NodeRestInfo(object):
    interface.implements(IRestAction)

    title = 'Content information'
    description = ''

    __permission__ = View

    def __call__(self, content, request, *args):
        info = cms(content).info()
        info['__link__'] = '%s%s/'%(request.application_url, content.__uri__)
        return info


class ContainerRestInfo(NodeRestInfo):

    title = 'Container information'
    description = ''

    __permission__ = View

    def __call__(self, content, request, *args):
        info = super(ContainerRestInfo, self).__call__(content, request)

        contents = []
        for item in content.values():
            if not ptah.checkPermission(
                self.__permission__, item, request, False):
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
        info['__container__'] = True
        return info


class ContentAPIDoc(NodeRestInfo):

    title = 'API Doc'
    description = ''

    __permission__ = View

    def __call__(self, content, request, *args):
        info = super(ContentAPIDoc, self).__call__(content, request)

        info['__actions__'] = []

        actions = []
        url = request.application_url
        for name, action in request.registry.adapters.lookupAll(
            (IRestActionClassifier, providedBy(content)), IRestAction):

            if not ptah.checkPermission(
                action.__permission__, content, request, False):
                continue

            actions.append(
                (name, action.title,
                 OrderedDict(
                     (('name', name or 'info'),
                      ('link', '%s%s/%s'%(url, content.__uri__, name)),
                      ('title', action.title),
                      ('description', action.description)))))

        actions.sort()
        info['__actions__'] = [action for _t, _n, action in actions]

        return info


class DeleteAction(object):

    title = 'Delete content'
    description = ''

    __permission__ = DeleteContent

    def __call__(self, content, request, *args):
        content.delete()


class MoveAction(object):

    title = 'Move content'
    description = ''

    __permission__ = ModifyContent

    def __call__(self, content, request, *args):
        pass


class UpdateAction(NodeRestInfo):

    title = 'Update content'
    description = ''

    __permission__ = ModifyContent

    def __call__(self, content, request, *args):
        tinfo = content.__type__

        try:
            data = tinfo.schema.deserialize(request.POST)
        except colander.Invalid, e:
            request.response.status = 500
            return {'errors': e.asdict()}

        content.update(**data)

        return super(UpdateAction, self).__call__(content, request)


class CreateContentAction(object):

    title = 'Create content'
    description = ''

    __permission__ = View

    def __call__(self, content, request, uri='', *args):
        name = request.GET.get('name')
        tinfo = request.GET.get('tinfo')

        item = cms(content).create(tinfo, name)

        tinfo = item.__type__
        try:
            data = tinfo.schema.deserialize(request.POST)
        except colander.Invalid, e:
            request.response.status = 500
            return {'errors': e.asdict()}

        item.update(**data)
        return NodeRestInfo()(item, request)


class BlobData(object):
    interface.implements(IRestAction)

    title = 'Download blob'
    description = ''

    __permission__ = View

    def __call__(self, content, request, *args):
        response = request.response
        response.content_type = content.mimetype.encode('utf-8')
        if content.filename:
            response.headerlist = {
                'Content-Disposition': 
                'filename="%s"'%content.filename.encode('utf-8')}
        response.body = content.read()
        return response


contentRestAction('data', IBlob, BlobData())

contentRestAction('', IContent, NodeRestInfo())
contentRestAction('', IContainer, ContainerRestInfo())
contentRestAction('apidoc', IContent, ContentAPIDoc())
contentRestAction('update', IContent, UpdateAction())
contentRestAction('delete', IContent, DeleteAction())
contentRestAction('move', IContent, MoveAction())
contentRestAction('create', IContainer, CreateContentAction())

ptah.registerService('cms', 'cms', 'Ptah CMS api')
ptah.registerServiceAction('cms', Content())
ptah.registerServiceAction('cms', Applications())
ptah.registerServiceAction('cms', Types())
