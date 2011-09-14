""" rest api for cms """
import ptah
import sqlalchemy as sqla

from ptah_cms.node import Session
from ptah_cms.container import Container


class Applications(ptah.rest.Action):

    name = 'applications'
    title = 'List applications'
    
    _sql_get_roots = ptah.QueryFreezer(
        lambda: Session.query(Container)\
            .filter(sqla.sql.and_(Container.__type_id__=='application')))

    def __call__(self, request, *args):
        apps = {}

        for root in self._sql_get_roots.all():
            print root
            apps[root.name] = {
                'name': root.name,
                'path': root.__path__,
                'uuid': root.__uuid__,
                }

        return apps


class Content(ptah.rest.Action):

    name = 'content'
    title = 'CMS Content'

    def __call__(self, request, uuid, *args):
        info = {}

        content = ptah.resolve(uuid)
        
        if isinstance(content, Container):
            container = True
            path = content.__path__
        else:
            container = False
            path = '%s%s'%(content.__parent_ref__.__path__, content.__name__)
        
        print content
        info = {'__name__': content.name,
                '__path__': path,
                '__type__': content.__type_id__,
                '__uuid__': content.__uuid__,
                '__container__': container,
                }

        return info


ptah.rest.registerService('cms', 'cms', 'Ptah CMS api')
ptah.rest.registerServiceAction('cms', Content())
ptah.rest.registerServiceAction('cms', Applications())
