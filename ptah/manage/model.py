""" content types module """
from pyramid.view import view_config
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah import cms, form
from ptah.manage import get_manage_url


@ptah.manage.module('models')
class ModelModule(ptah.manage.PtahModule):
    __doc__ = 'A listing of all registered models.'

    title = 'Models'

    def __getitem__(self, key):
        ti = cms.get_type('cms-type:%s'%key)

        if ti is not None:
            return Model(ti, self, self.request)

        raise KeyError(key)

    def available(self):
        return bool(cms.get_types())


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

        self.record = ptah.get_session().query(tinfo.cls)\
            .filter(tinfo.cls.__id__ == pid).one()


@view_config(
    context=ModelModule, wrapper=ptah.wrap_layout(),
    renderer='ptah.manage:templates/models.pt')

class ModelModuleView(ptah.View):

    rst_to_html = staticmethod(ptah.rst_to_html)

    def update(self):
        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.request.registry)

        types = []
        for ti in cms.get_types().values():
            if ti.__uri__ in cfg['disable_models']:
                continue
            types.append((ti.title, ti))

        self.types = [f for _t, f in sorted(types)]


@view_config(
    context=Model, wrapper=ptah.wrap_layout(),
    renderer='ptah.manage:templates/model.pt')

class ModelView(form.Form):

    csrf = True
    page = ptah.Pagination(15)

    def update(self):
        tinfo = self.context.tinfo
        cls = tinfo.cls

        self.fields = tinfo.fieldset

        result = super(ModelView, self).update()

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

        Session = ptah.get_session()

        self.size = Session.query(cls).count()
        self.current = current

        self.pages, self.prev, self.next = self.page(self.size, self.current)

        offset, limit = self.page.offset(current)
        self.data = Session.query(cls)\
            .order_by(cls.__id__).offset(offset).limit(limit).all()

        return result

    def get_record_info(self, item):
        res = {}
        for field in self.widgets.fields():
            val = getattr(item, field.name, field.default)
            res[field.name] = field.serialize(val)

        return res

    @form.button('Add', actype=form.AC_PRIMARY)
    def add(self):
        return HTTPFound(location='add.html')

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

        Session = ptah.get_session()
        for rec in Session.query(self.context.tinfo.cls).filter(
            self.context.tinfo.cls.__id__.in_(ids)).all():
            Session.delete(rec)

        self.message('Select records have been removed.')
        return HTTPFound(location = self.request.url)


@view_config(
    'add.html',
    context=Model, wrapper=ptah.wrap_layout(),
    renderer='ptah.manage:templates/model-add.pt')

class AddRecord(form.Form):
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

        Session = ptah.get_session()
        Session.add(record)
        Session.flush()

        self.message('New record has been created.', 'success')
        return HTTPFound(location='./%s/'%record.__id__)

    @form.button('Back')
    def back_handler(self):
        return HTTPFound(location='.')


@view_config(
    context=Record, wrapper=ptah.wrap_layout(),
    renderer='ptah.manage:templates/model-edit.pt')

class EditRecord(form.Form):
    __doc__ = "Edit model record."

    csrf = True

    @reify
    def label(self):
        return 'Record id: %s'%self.context.__name__

    @reify
    def fields(self):
        return self.context.tinfo.fieldset

    def update(self):
        self.manage = get_manage_url(self.request)
        return super(EditRecord, self).update()

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
        return HTTPFound(location='../')
