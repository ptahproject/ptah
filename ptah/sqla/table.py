import ptah
import pyramid_sqla
from memphis import view, form
from webob.exc import HTTPFound

from module import Session
from interfaces import ITable


class TableView(form.Form):
    view.pyramidView(
        'index.html', ITable, route='ptah-manage', default = True,
        template = view.template('ptah.sqla:templates/table.pt'))

    bsize = 15

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

        total = int(round(self.size/float(self.bsize)+0.5))
        batches = range(1, total+1)

        self.total = total
        self.current = current

        self.hasNext = current != total
        self.hasPrev = current > 1

        self.prevLink = current if not self.hasPrev else current-1
        self.nextLink = current if not self.hasNext else current+1

        self.batches = ptah.first_neighbours_last(batches, current-1, 3, 3)

        self.data = Session.query(table)\
            .offset((current-1)*self.bsize).limit(self.bsize).all()

    def pageInfo(self, idx):
        if idx is None:
            return 'disabled', '...'
        elif idx == self.current:
            return 'active', idx
        else:
            return '', idx

    @form.button('Add', actype=form.AC_PRIMARY)
    def add(self):
        raise HTTPFound(location='add.html')

    @form.button('Remove', actype=form.AC_DANGER)
    def remove(self):
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

        
