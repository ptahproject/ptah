""" content types module """
import ptah
from ptah import cms, view, form, manage

from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

class ModelModule(manage.PtahModule):
    __doc__ = u'A listing of all registered models.'

    title = 'Models'
    manage.module('models')

    def __getitem__(self, key):
        ti = cms.get_type('cms-type:%s'%key)

        if ti is not None:
            return Model(ti, self, self.request)

        raise KeyError(key)


class Model(object):

    def __init__(self, tinfo, context, request):
        self.__name__ = tinfo.name
        self.__parent__ = context
        self.request = request
        self.tinfo = tinfo

    def __getitem__(self, key):
        if key == 'add.html':
            raise KeyError(key)

        try:
            return Record(key, self.tinfo, self, self.request)
        except:
            raise KeyError(key)


class Record(object):

    def __init__(self, pid, tinfo, parent, request):
        self.__name__ = str(pid)
        self.__parent__ = parent

        self.pid = pid
        self.tinfo = tinfo
        self.cls = tinfo.cls
        self.request = request

        self.record = cms.Session.query(tinfo.cls)\
            .filter(tinfo.cls.__id__ == pid).one()


class ModelModuleView(view.View):
    view.pview(context = ModelModule,
               template = view.template('ptah.manage:templates/models.pt'))

    rst_to_html = staticmethod(ptah.rst_to_html)

    def update(self):
        types = []
        for ti in cms.get_types().values():
            if ti.__uri__ in manage.CONFIG['disable_models']:
                continue
            types.append((ti.title, ti))
        types.sort()
        self.types = [f for _t, f in types]


class ModelView(form.Form):
    view.pview(context = Model,
               template = view.template('ptah.manage:templates/model.pt'))

    csrf = True
    page = ptah.Pagination(15)

    def update(self):
        tinfo = self.context.tinfo
        cls = tinfo.cls

        self.fields = tinfo.fieldset

        super(ModelView, self).update()

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

        self.size = cms.Session.query(cls).count()
        self.current = current

        self.pages, self.prev, self.next = self.page(self.size, self.current)

        offset, limit = self.page.offset(current)
        self.data = cms.Session.query(cls)\
            .order_by(cls.__id__).offset(offset).limit(limit).all()

    def get_record_info(self, item):
        res = {}
        for field in self.widgets.fields():
            val = getattr(item, field.name, field.default)
            res[field.name] = field.serialize(val)

        return res

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
            except: # pragma: no cover
                pass

        if not ids:
            self.message('Please select records for removing.', 'warning')
            return

        for rec in cms.Session.query(self.context.tinfo.cls).filter(
            self.context.tinfo.cls.__id__.in_(ids)).all():
            cms.Session.delete(rec)

        self.message('Select records have been removed.')
        raise HTTPFound(location = self.request.url)


class AddRecord(form.Form):
    view.pview('add.html',
               context = Model,
               template = view.template('ptah.manage:templates/model-add.pt'))

    __doc__ = "Add model record."

    csrf = True

    @reify
    def fields(self):
        return self.context.tinfo.fieldset

    @form.button('Add', actype=form.AC_PRIMARY)
    def add_handler(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        self.record = record = self.context.tinfo.create()

        if hasattr(record, 'update'):
            record.update(**data)
        else:
            for field in self.context.tinfo.fieldset.fields():
                val = data.get(field.name, field.default)
                if val is not form.null:
                    setattr(record, field.name, val)

        cms.Session.add(record)
        cms.Session.flush()

        self.message('New record has been created.', 'success')
        raise HTTPFound(location='./%s/'%record.__id__)

    @form.button('Back')
    def back_handler(self):
        raise HTTPFound(location='.')


class EditRecord(form.Form):
    view.pview(context = Record,
               template = view.template('ptah.manage:templates/model-edit.pt'))

    __doc__ = "Edit model record."

    csrf = True

    @reify
    def label(self):
        return 'Record id: %s'%self.context.__name__

    @reify
    def fields(self):
        return self.context.tinfo.fieldset

    def update(self):
        self.manage_url = manage.CONFIG.manage_url
        super(EditRecord, self).update()

    def form_content(self):
        data = {}
        for field in self.fields.fields():
            data[field.name] = getattr(
                self.context.record, field.name, field.default)
        return data

    @form.button('Modify', actype=form.AC_PRIMARY)
    def modify_handler(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        record = self.context.record

        if hasattr(record, 'update'):
            record.update(**data)
        else:
            for field in self.fields.fields():
                val = data.get(field.name, field.default)
                if val is not form.null:
                    setattr(record, field.name, val)

        self.message('Model record has been modified.', 'success')

    @form.button('Back')
    def back_handler(self):
        raise HTTPFound(location='../')


class TypeIntrospection(object):
    """ Ptah content types """

    name = 'ptah-cms:type'
    title = 'Content Types'
    manage.introspection('ptah-cms:type')

    actions = view.template('ptah.manage:templates/directive-type.pt')

    def __init__(self, request):
        self.request = request

    def renderActions(self, *actions):
        return self.actions(
            types = cms.get_types(),
            actions = actions,
            rst_to_html = ptah.rst_to_html,
            manage_url = manage.CONFIG.manage_url,
            request = self.request)
