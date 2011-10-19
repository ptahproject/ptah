""" introspect module """
import ptah
import sqlahelper as psa
from ptah import config, view, form, manage
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

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
        tables = []

        for id, (md, title) in self.context.metadata.items():
            data = []
            for name, table in md.tables.items():
                data.append((name, self.printTable(table)))

            data.sort()
            tables.append((title, id, data))

        tables.sort()
        self.tables = tables


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
        for cl in table.columns:
            if cl.primary_key:
                self.primary = cl.name
                self.pcolumn = cl

        super(TableView, self).update()

        request = self.request
        try:
            current = int(request.params.get('batch', None))
            if not current:
                current = request.session.get('table-current-batch')
                if not current:
                    current = 1
            else:
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
            self.message('Please select records for removing', 'warning')
            return

        self.table.delete(self.pcolumn.in_(ids)).execute()
        self.message('Select records have been removed')


class EditRecord(form.Form):
    view.pview(context = Record)

    __doc__ = "Edit table record."
    __intr_path__ = '/ptah-manage/sqla/${table}/${record}/index.html'

    csrf = True

    @reify
    def label(self):
        return '%s: record %s'%(self.context.table.name, self.context.__name__)

    @reify
    def fields(self):
        return ptah.buildSqlaFieldset(
            [(cl.name, cl) for cl in self.context.table.columns])

    def form_content(self):
        data = {}
        for field in self.fields.fields():
            data[field.name] = getattr(
                self.context.data, field.name, field.default)
        return data

    @form.button('Cancel')
    def modify(self):
        raise HTTPFound(location='../')

    @form.button('Modify', actype=form.AC_PRIMARY)
    def modify(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        self.context.table.update(
            self.context.pcolumn == self.context.__name__, data).execute()
        self.message('Table record has been modified.', 'success')
        raise HTTPFound(location='../')

    @form.button('Remove', actype=form.AC_DANGER)
    def remove(self):
        self.validate_csrf_token()

        self.context.table.delete(
            self.context.pcolumn == self.context.__name__).execute()
        self.message('Table record has been removed.')
        raise HTTPFound(location='../')


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
        return ptah.buildSqlaFieldset(
            [(cl.name, cl) for cl in self.context.table.columns])

    @form.button('Create', actype=form.AC_PRIMARY)
    def create(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        try:
            self.context.table.insert(values = data).execute()
        except Exception, e:
            self.message(e, 'error')
            return

        self.message('Table record has been created.', 'success')
        raise HTTPFound(location='./')

    @form.button('Save & Create new', actype=form.AC_PRIMARY)
    def create_multiple(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        try:
            self.context.table.insert(values = data).execute()
        except Exception, e:
            self.message(e, 'error')
            return

        self.message('Table record has been created.', 'success')

    @form.button('Back')
    def cancel(self):
        raise HTTPFound(location='./')
