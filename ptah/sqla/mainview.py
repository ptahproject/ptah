import ptah
from zope import interface
from webob.exc import HTTPFound
from memphis import config, view

import pyramid_sqla as psa

from interfaces import ISQLAModule

Base = psa.get_base()


class MainView(view.View):
    view.pyramidView(
        'index.html', ISQLAModule, 'ptah-manage', default=True, layout='',
        template = view.template(
            'ptah.sqla:templates/index.pt', nolayer=True))

    __doc__ = "sqlalchemy tables listing page."
    __intr_path__ = '/ptah-manage/sqla/index.html'

    def printTable(self, table):
        columns = []
        for cl in table.columns:
            kwarg = []
            if cl.key != cl.name:
                kwarg.append('key')
            if cl.primary_key:
                kwarg.append('primary_key')
            if not cl.nullable:
                kwarg.append('nullable')
            if cl.onupdate:
                kwarg.append('onupdate')
            if cl.default:
                kwarg.append('default')
            if cl.server_default:
                kwarg.append('server_default')

            columns.append(
                "Column(%s)" % ', '.join(
                    [repr(cl.name)] + [repr(cl.type)] +
                    [repr(x) for x in cl.foreign_keys if x is not None] +
                    [repr(x) for x in cl.constraints] +
                    ["%s=%s" % (k, repr(getattr(cl, k))) for k in kwarg])
                )

        return ("Table(%s)" % repr(table.name), columns)

    def update(self):
        Base = psa.get_base()

        tables = []

        for name, table in Base.metadata.tables.items():
            tables.append((name, self.printTable(table)))

        tables.sort()
        self.tables = tables
