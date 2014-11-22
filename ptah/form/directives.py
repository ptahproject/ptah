"""
Pyramid directives
"""
import venusian
from pyramid.registry import Introspectable

ID_FIELD = 'ptah.form:field'
ID_PREVIEW = 'ptah.form:field-preview'


def add_field(cfg, name, cls):
    """ Field registration directive. Field should be inherited from
    :py:class:`ptah.form.Field` class.

    .. code-block:: python

      class TextField(ptah.form.Field):
          ...


      config = Configurator(...)
      config.include('ptah.form')

      config.provide_form_field('text', TextField)

    """
    discr = (ID_FIELD, name)

    intr = Introspectable(ID_FIELD, discr, name, 'ptah.form-field')
    intr['name'] = name
    intr['field'] = cls

    cls.__field__ = name

    def action():
        storage = cfg.registry.get(ID_FIELD)
        if storage is None:
            storage = cfg.registry[ID_FIELD] = {}

        storage[name] = cls

    cfg.action(discr, action, introspectables=(intr,))


class field(object):

    def __init__(self, name):
        self.name = name

    def __call__(self, wrapped):
        def callback(context, name, ob):
            cfg = context.config.with_package(info.module)
            add_field(cfg, self.name, ob)

        info = venusian.attach(wrapped, callback, category='ptah.form')
        return wrapped


def add_fieldpreview(cfg, cls, callable):
    discr = (ID_PREVIEW, cls)

    intr = Introspectable(
        ID_PREVIEW, discr, 'Field preview for "%s"'%cls, 'ptah.form-preview')
    intr['field'] = cls
    intr['preview'] = callable

    def action():
        storage = cfg.registry.get(ID_PREVIEW)
        if storage is None:
            storage = cfg.registry[ID_PREVIEW] = {}

        storage[cls] = callable

    cfg.action(discr, action, introspectables=(intr,))


class fieldpreview(object):
    """Register fieldpreview factory for field class.
    Fieldpreview factory is used in ``Field types`` management module.
    It should be an object that implements the
    :py:class:`ptah.form.interfaces.Preview` interface.

    .. code-block:: python

      @form.fieldpreview(form.TextField)
      def textPreview(request):
          field = form.TextField(
              'TextField',
              title = 'Text field',
              description = 'Text field preview description',
              default = 'Test text in text field.')

          widget = field.bind(request, 'preview.', form.null, {})
          widget.update()
          return ptah.renderer.render(request, 'form:widget', widget)

    """
    def __init__(self, cls):
        self.cls = cls

    def __call__(self, wrapped):
        def callback(context, name, ob):
            cfg = context.config.with_package(info.module)
            add_fieldpreview(cfg, self.cls, ob)

        info = venusian.attach(wrapped, callback, category='ptah.form')
        return wrapped


def get_field_factory(request, name):
    """Return field factory by name."""
    return request.registry[ID_FIELD][name]


def get_field_preview(request, cls):
    """Return field preview factory for field class."""
    return request.registry[ID_PREVIEW][cls]
