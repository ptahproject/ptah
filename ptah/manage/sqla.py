""" sqla module """
import urllib
from sqlalchemy.orm.mapper import _mapper_registry
from pyramid.view import view_config
from pyramid.compat import url_quote_plus
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah import form

Session = ptah.get_session()


@ptah.manage.module('sqla')
class SQLAModule(ptah.manage.PtahModule):
    __doc__ = 'A listing of all tables with ability to view and edit records'

    title = 'SQLAlchemy'

    metadata = {}

    def __getitem__(self, key):
        try:
            id, table = key.split('-', 1)
        except:
            raise KeyError(key)

        md = self.metadata[id][0]
        return Table(md.tables[table], self, self.request)

    @classmethod
    def addMetadata(cls, md, id, title=''):
        cls.metadata[id] = [md, title or id.capitalize()]

addMetadata = SQLAModule.addMetadata
addMetadata(ptah.get_base().metadata, 'psqla', 'Pyramid sqla')


class Table(object):

    def __init__(self, table, mod, request):
        self.__name__ = table.name
        self.__parent__ = mod

        self.table = table
        self.request = request

    def __getitem__(self, key):
        if key == 'add.html':
            raise KeyError(key)

        try:
            return Record(key, self.table, self, self.request)
        except:
            raise KeyError(key)


class Record(object):

    def __init__(self, pid, table, parent, request):
        self.pid = pid
        self.table = table
        self.request = request

        self.__name__ = str(pid)
        self.__parent__ = parent

        self.pname = None
        self.pcolumn = None
        for cl in table.columns:
            if cl.primary_key:
                self.pname = cl.name
                self.pcolumn = cl

        self.data = Session.query(table).filter(
            self.pcolumn == pid).one()


@view_config(
    context=SQLAModule, wrapper=ptah.wrap_layout(),
    renderer='ptah.manage:templates/sqla-index.pt')

class MainView(ptah.View):
    __doc__ = "sqlalchemy tables listing page."

    def printTable(self, table):
        columns = []
        for cl in table.columns:
            kwarg = []
            if cl.key != cl.name:
                kwarg.append('key') # pragma: no cover
            if cl.primary_key:
                kwarg.append('primary_key')
            if not cl.nullable:
                kwarg.append('nullable')
            if cl.default:
                kwarg.append('default')

            columns.append(
                "Column(%s)" % ', '.join(
                    [repr(cl.name)] + [repr(cl.type)] +
                    [repr(x) for x in cl.foreign_keys if x is not None] +
                    [repr(x) for x in cl.constraints] +
                    ["%s=%s" % (k, repr(getattr(cl, k))) for k in kwarg])
                )

        return ("Table(%s)" % repr(table.name), columns)

    def update(self):
        tables = []

        for id, (md, title) in self.context.metadata.items():
            data = []
            for name, table in md.tables.items():
                data.append((name, self.printTable(table)))

            tables.append((title, id, sorted(data)))

        self.tables = sorted(tables)


def get_inheritance(table):
    # inheritance
    inherits = []
    mapper = None
    for m, s in _mapper_registry.items():
        if m.local_table is table:
            mapper = m

    curr_mapper = mapper
    while curr_mapper is not None:
        curr_mapper = curr_mapper.inherits
        if curr_mapper is not None and \
                curr_mapper.local_table.name != table.name and \
                curr_mapper.local_table.name not in inherits:
            inherits.append(curr_mapper.local_table.name)

    inherits.reverse()
    return inherits


@view_config(
    context=Table, wrapper=ptah.wrap_layout(),
    renderer='ptah.manage:templates/sqla-table.pt')

class TableView(ptah.form.Form):
    __doc__ = "List table records."

    csrf = True
    page = ptah.Pagination(15)

    def update(self):
        table = self.table = self.context.table
        self.primary = None
        self.pcolumn = None
        self.uris = []

        self.inheritance = get_inheritance(table)

        if table.name == 'ptah_nodes' or self.inheritance:
            self.show_actions = False
        else:
            self.show_actions = True

        names = []
        for cl in table.columns:
            names.append(cl.name)
            if cl.primary_key:
                self.primary = cl.name
                self.pcolumn = cl
            if cl.info.get('uri'):
                self.uris.append(len(names)-1)

        res = super(TableView, self).update()

        request = self.request
        try:
            current = int(request.params.get('batch', None))
            if not current:
                current = 1

            request.session['table-current-batch'] = current
        except:
            current = request.session.get('table-current-batch')
            if not current:
                current = 1

        self.size = Session.query(table).count()
        self.current = current

        self.pages, self.prev, self.next = self.page(self.size, self.current)

        offset, limit = self.page.offset(current)
        self.data = Session.query(table).offset(offset).limit(limit).all()

        return res

    def quote(self, val):
        return url_quote_plus(val)

    def val(self, val):
        try:
            if isinstance(val, str): # pragma: no cover
                val = unicode(val, 'utf-8', 'ignore')
            elif not isinstance(val, unicode):
                val = str(val)
        except: # pragma: no cover
            val = "Can't show"
        return val[:100]

    @ptah.form.button('Add', actype=ptah.form.AC_PRIMARY)
    def add(self):
        return HTTPFound(location='add.html')

    @ptah.form.button('Remove', actype=ptah.form.AC_DANGER)
    def remove(self):
        self.validate_csrf_token()

        ids = []
        for id in self.request.POST.getall('rowid'):
            ids.append(id)

        if not ids:
            self.message('Please select records for removing.', 'warning')
            return

        self.table.delete(self.pcolumn.in_(ids)).execute()
        self.message('Select records have been removed.')


@view_config(
    context=Record, wrapper=ptah.wrap_layout(),
    renderer='ptah.manage:templates/sqla-edit.pt')

class EditRecord(ptah.form.Form):
    __doc__ = "Edit table record."

    csrf = True

    @reify
    def label(self):
        return 'record %s'%self.context.__name__

    @reify
    def fields(self):
        return ptah.build_sqla_fieldset(
            [(cl.name, cl) for cl in self.context.table.columns],
            skipPrimaryKey=True)

    def update(self):
        self.inheritance = get_inheritance(self.context.table)
        if self.context.table.name == 'ptah_nodes' or self.inheritance:
            self.show_remove = False
        else:
            self.show_remove = True

        return super(EditRecord, self).update()

    def form_content(self):
        data = {}
        for field in self.fields.fields():
            data[field.name] = getattr(
                self.context.data, field.name, field.default)
        return data

    @ptah.form.button('Cancel')
    def cancel_handler(self):
        return HTTPFound(location='..')

    @ptah.form.button('Modify', actype=ptah.form.AC_PRIMARY)
    def modify_handler(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        self.context.table.update(
            self.context.pcolumn == self.context.__name__, data).execute()
        self.message('Table record has been modified.', 'success')
        return HTTPFound(location='..')

    @ptah.form.button('Remove', actype=ptah.form.AC_DANGER,
                      condition=lambda form: form.show_remove)
    def remove_handler(self):
        self.validate_csrf_token()

        self.context.table.delete(
            self.context.pcolumn == self.context.__name__).execute()
        self.message('Table record has been removed.')
        return HTTPFound(location='..')



@view_config('add.html', context=Table, wrapper=ptah.wrap_layout())

class AddRecord(ptah.form.Form):
    """ Add new table record. """

    csrf = True

    @reify
    def label(self):
        return '%s: new record'%self.context.table.name

    @reify
    def fields(self):
        return ptah.build_sqla_fieldset(
            [(cl.name, cl) for cl in self.context.table.columns],
            skipPrimaryKey = True)

    @ptah.form.button('Create', actype=ptah.form.AC_PRIMARY)
    def create(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        try:
            self.context.table.insert(values = data).execute()
        except Exception as e: # pragma: no cover
            self.message(e, 'error')
            return

        self.message('Table record has been created.', 'success')
        return HTTPFound(location='.')

    @ptah.form.button('Save & Create new',
                      name='createmulti', actype=ptah.form.AC_PRIMARY)
    def create_multiple(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        try:
            self.context.table.insert(values = data).execute()
        except Exception as e: # pragma: no cover
            self.message(e, 'error')
            return

        self.message('Table record has been created.', 'success')

    @ptah.form.button('Back')
    def cancel(self):
        return HTTPFound(location='.')
