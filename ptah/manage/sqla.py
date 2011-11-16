""" introspect module """
import urllib
import sqlahelper as psa
from sqlalchemy.orm.mapper import _mapper_registry
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah import view, form, manage

Session = psa.get_session()
metadata = psa.get_base().metadata


class SQLAModule(manage.PtahModule):
    __doc__ = u'A listing of all tables with ability to view and edit records'

    title = 'SQLAlchemy'
    manage.module('sqla')

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
addMetadata(metadata, 'psqla', 'Pyramid sqla')


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


class MainView(view.View):
    view.pview(
        context = SQLAModule,
        template = view.template('ptah.manage:templates/sqla-index.pt'))

    __doc__ = "sqlalchemy tables listing page."
    __intr_path__ = '/ptah-manage/sqla/index.html'

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

            data.sort()
            tables.append((title, id, data))

        tables.sort()
        self.tables = tables


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
                curr_mapper.local_table.name != table.name:
            inherits.append(curr_mapper.local_table.name)

    inherits.reverse()
    return inherits


class TableView(form.Form):
    view.pview(
        context = Table,
        template = view.template('ptah.manage:templates/sqla-table.pt'))

    __doc__ = "List table records."
    __intr_path__ = '/ptah-manage/sqla/${table}/index.html'

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

        super(TableView, self).update()

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

    def quote(self, val):
        return urllib.quote_plus(val)

    def val(self, val):
        try:
            if isinstance(val, str): # pragma: no cover
                val = unicode(val, 'utf-8', 'ignore')
            elif not isinstance(val, unicode):
                val = str(val)
        except: # pragma: no cover
            val = u"Can't show"
        return val[:100]

    @form.button('Add', actype=form.AC_PRIMARY)
    def add(self):
        raise HTTPFound(location='add.html')

    @form.button('Remove', actype=form.AC_DANGER)
    def remove(self):
        self.validate_csrf_token()

        ids = []
        for id in self.request.POST.getall('rowid'):
            try:
                ids.append(int(id))
            except:
                pass

        if not ids:
            self.message('Please select records for removing.', 'warning')
            return

        self.table.delete(self.pcolumn.in_(ids)).execute()
        self.message('Select records have been removed.')


class EditRecord(form.Form):
    view.pview(context = Record,
               template = view.template('ptah.manage:templates/sqla-edit.pt'))

    __doc__ = "Edit table record."
    __intr_path__ = '/ptah-manage/sqla/${table}/${record}/index.html'

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

        super(EditRecord, self).update()

    def form_content(self):
        data = {}
        for field in self.fields.fields():
            data[field.name] = getattr(
                self.context.data, field.name, field.default)
        return data

    @form.button('Cancel')
    def cancel_handler(self):
        raise HTTPFound(location='..')

    @form.button('Modify', actype=form.AC_PRIMARY)
    def modify_handler(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        self.context.table.update(
            self.context.pcolumn == self.context.__name__, data).execute()
        self.message('Table record has been modified.', 'success')
        raise HTTPFound(location='..')

    @form.button('Remove', actype=form.AC_DANGER,
                 condition=lambda form: form.show_remove)
    def remove_handler(self):
        self.validate_csrf_token()

        self.context.table.delete(
            self.context.pcolumn == self.context.__name__).execute()
        self.message('Table record has been removed.')
        raise HTTPFound(location='..')


class AddRecord(form.Form):
    """ Add new table record. """
    view.pview('add.html', Table)

    __intr_path__ = '/ptah-manage/sqla/${table}/add.html'

    csrf = True

    @reify
    def label(self):
        return '%s: new record'%self.context.table.name

    @reify
    def fields(self):
        return ptah.build_sqla_fieldset(
            [(cl.name, cl) for cl in self.context.table.columns],
            skipPrimaryKey = True)

    @form.button('Create', actype=form.AC_PRIMARY)
    def create(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        try:
            self.context.table.insert(values = data).execute()
        except Exception, e: # pragma: no cover
            self.message(e, 'error')
            return

        self.message('Table record has been created.', 'success')
        raise HTTPFound(location='.')

    @form.button('Save & Create new', name='createmulti',actype=form.AC_PRIMARY)
    def create_multiple(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        try:
            self.context.table.insert(values = data).execute()
        except Exception, e: # pragma: no cover
            self.message(e, 'error')
            return

        self.message('Table record has been created.', 'success')

    @form.button('Back')
    def cancel(self):
        raise HTTPFound(location='.')
