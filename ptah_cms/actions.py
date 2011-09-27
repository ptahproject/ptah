""" default content actions """
import colander
from memphis import config

import ptah
from ptah_cms.cms import action, registerAction
from ptah_cms.events import ContentModifiedEvent
from ptah_cms.container import Container
from ptah_cms.permissions import View, DeleteContent, ModifyContent
from ptah_cms.interfaces import ContentSchema
from ptah_cms.interfaces import IContent, IContainer
from ptah_cms.interfaces import Error, NotFound, Forbidden


@action('delete', IContent, DeleteContent, title='Delete content')
def delete(content):
    parent = content.__parent__
    if not isinstance(parent, Container):
        raise Error("Can't remove content from non container")

    del parent[content]


@action('batchdelete', IContainer, DeleteContent, title='Batch delete')
def batchdelete(content, uris):
    raise NotImplements()


@action('create', IContent, title='Create content')
def create(content, tname, name):
    if not isinstance(content, Container):
        raise Error('Can create content only in container.')

    tinfo = ptah.resolve(tname)
    if tinfo is None:
        raise NotFound('Type information is not found')

    tinfo.checkContext(content)

    if '/' in name:
        raise Error("Names cannot contain '/'")

    if name.startswith(' '):
        raise Error("Names cannot starts with ' '")

    content[name] = tinfo.create()
    return content[name]


@action('update', IContent, ModifyContent, title='Update content')
def update(content, **data):
    tinfo = content.__type__

    for node in tinfo.schema:
        val = data.get(node.name, node.default)
        if val is not colander.null:
            setattr(content, node.name, val)

    config.notify(ContentModifiedEvent(content))


class ContentInfo(object):

    def loadInfo(self, info, content):
        for node in content.__type__.schema:
            val = getattr(content, node.name, node.missing)
            try:
                info[node.name] = node.serialize(val)
            except:
                info[node.name] = node.default

        info['view'] = content.view
        info['created'] = content.created
        info['modified'] = content.modified
        info['effective'] = content.effective
        info['expires'] = content.expires

    def __call__(self, content):
        info = OrderedDict(
            (('__name__', content.__name__),
             ('__type__', content.__type_id__),
             ('__uri__', content.__uri__),
             ('__container__', False),
             ('__link__', '%s%s/'%(request.application_url, content.__uri__)),
             ('__parents__', parents(content)),
             ))

        self.loadInfo(info, content)

        return info

registerAction('info', ContentInfo(), IContent, View, 'Content information')
