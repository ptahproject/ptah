import ptah
import logging

log = logging.getLogger('ptah')


class Form(ptah.form.Form):

    errors = None

    def __init__(self, mtype, payload, protocol):
        super(Form, self).__init__(protocol, protocol.request)

        self.mtype = mtype
        self.params = payload
        self.protocol = protocol

    def __call__(self):
        self.update()

        if '__validate__' in self.params:
            data, errors = self.extract()
            if errors:
                errs = {}
                for err in errors:
                    if err.field is not None:
                        errs[err.field.name] = err.msg

                self.protocol.send(self.mtype, {'errors': errs})
                return

        if '__action__' in self.params:
            action = self.params['__action__']
            handler = self.actions.get(action)
            if handler is not None:
                self.errors = handler(self)
                if not self.errors:
                    return
            else:
                log.warning("Can't find '%s' message handler", action)

        self.protocol.send(self.mtype, self.render())

    def get_msg_data(self):
        return {}

    def close(self, msg=None):
        if msg:
            self.protocol.send(
                self.mtype,
                {'__close__': True,
                 'message': ptah.render_message(self.request, msg)})
        else:
            self.protocol.send(self.mtype, {'__close__': True})

    def render(self):
        data = self.get_msg_data()
        data.update({'id': self.id,
                     'name': self.name,
                     'label': self.label or None,
                     'description': self.description,
                     'fieldsets': []})

        data['actions'] = actions = []
        for name, ac in self.actions.items():
            actions.append({'name': name,
                            'title': ac.title,
                            'cls': ac.klass})

        if self.errors:
            data['errors'] = ptah.render_message(
                self.request, self.errors, 'form-error')

        request = self.request

        fieldsets = data['fieldsets']
        for fieldset in self.widgets.fieldsets:
            widgets = []
            fieldsets.append(
                {'name': fieldset['name'],
                 'title': fieldset['title'] or None,
                 'widgets': widgets})

            for widget in fieldset['widgets']:
                widgets.append(
                    {'type': widget.__field__,
                     'id': widget.id,
                     'title': widget.title,
                     'description': widget.description,
                     'required': widget.required,
                     'error': getattr(getattr(widget,'error',None),'msg',None),
                     'field': widget.render(request),
                     })

        return data
