""" content traverser """
import ptah
from sqlalchemy import sql

from zope import interface
from memphis import config
from pyramid.interfaces import VH_ROOT_KEY, ITraverser
from pyramid.traversal import traversal_path, quote_path_segment

from node import Session
from container import Container
from interfaces import IApplicationRoot


class ContentTraverser(object):
    interface.implements(ITraverser)
    config.adapter(IApplicationRoot)

    _path_queries = {}

    def __init__(self, root):
        self.root = root

    def __call__(self, request, queries=_path_queries):
        environ = request.environ

        context = root = self.root
        path = environ.get('PATH_INFO','/') or '/'

        vroot_tuple = ()
        vpath = path
        vroot_idx = -1

        node, leaf = path.rsplit('/', 1)
        node = '%s/'%node

        if node == root.__path__:
            vpath_tuple = ()

            leaf = path[len(node):].split('/')
            leaf, subpath = leaf[0], leaf[1:]

            if leaf:
                leaf_c = root.get(leaf)
                if leaf_c is not None:
                    vpath_tuple += (leaf,)
                    if subpath:
                        leaf = subpath[0]
                        subpath = subpath[1:]
                    else:
                        leaf = ''
                    context = leaf_c

            return {'context': context,
                    'view_name': leaf,
                    'subpath': subpath,
                    'traversed': vpath_tuple,
                    'virtual_root': root,
                    'virtual_root_path': (),
                    'root': root}
        else:
            idx = 0
            paths = {}
            current = root.__path__
            for sec in path[len(root.__path__):].split('/'):
                if sec:
                    current = '%s%s/'%(current, sec)
                    paths[str(idx)] = current
                    idx += 1

            if idx not in queries:
                bindparams = [sql.bindparam(str(p)) for p in range(idx)]

                queries[idx] = ptah.QueryFreezer(
                    lambda: Session.query(Container)\
                        .filter(Container.__path__.in_(bindparams))
                        .order_by(sql.desc(Container.__path__)))

            parents = queries[idx].all(**paths)
            
            if parents:
                # set __parent__
                parents[-1].__parent__ = root
                for idx in range(len(parents)-1):
                    parents[idx].__parent__ = parents[idx+1]

                context = parents[0]
                node = parents[-1].__path__
                leaf = path[len(node):].split('/')
                leaf, subpath = leaf[0], leaf[1:]

                if node == path:
                    # this means PATH_INFO is path to contianer
                    return {'context': context,
                            'view_name': leaf,
                            'subpath': subpath,
                            'traversed': traversal_path(node),
                            'virtual_root': root,
                            'virtual_root_path': vroot_tuple,
                            'root': root}

                else:
                    # this means last element of PATH_INFO is
                    # leaf (content or view)
                    vpath_tuple = traversal_path(node)

                    if leaf:
                        leaf_c = context.get(leaf)
                        if leaf_c is not None:
                            vpath_tuple += (leaf,)
                            if subpath:
                                leaf = subpath[0]
                                subpath = subpath[1:]
                            else:
                                leaf = ''
                            context = leaf_c

                        return {'context': context,
                                'view_name': leaf,
                                'subpath': subpath,
                                'traversed': vpath_tuple,
                                'virtual_root': root,
                                'virtual_root_path': vroot_tuple,
                                'root': root}
            else:
                vpath_tuple = ()

                leaf = path[len(root.__path__):].split('/')
                leaf, subpath = leaf[0], leaf[1:]

                if leaf:
                    leaf_c = root.get(leaf)
                    if leaf_c is not None:
                        vpath_tuple += (leaf,)
                        if subpath:
                            leaf = subpath[0]
                            subpath = subpath[1:]
                        else:
                            leaf = ''
                        context = leaf_c

                return {'context': context,
                        'view_name': leaf,
                        'subpath': subpath,
                        'traversed': vpath_tuple,
                        'virtual_root': root,
                        'virtual_root_path': (),
                        'root': root}

            # not found
            return {'context': None,
                    'view_name': '',
                    'subpath': traversal_path(vpath),
                    'traversed': (),
                    'virtual_root': root,
                    'virtual_root_path': vroot_tuple,
                    'root': root}
