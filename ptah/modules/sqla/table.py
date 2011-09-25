import ptah
import pyramid_sqla
from memphis import view, form
from pyramid.httpexceptions import HTTPFound

from module import Session
from interfaces import ITable


class TableView(form.Form):
    view.pyramidView(
        'index.html', ITable, 'ptah-manage', default=True, layout='',
        template = view.template('ptah.modules.sqla:templates/table.pt'))

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
        self.validateToken()

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
