""" Widget implementation """
import colander
from zope import interface
from zope.component import getMultiAdapter
from zope.schema.interfaces import ITitledTokenizedTerm

from webob.multidict import MultiDict

from pagelets import FORM_INPUT
from interfaces import IWidget, IDataManager, ISequenceWidget, ITerms


PLACEHOLDER = object()


class Widget(object):
    """Widget base class."""
    interface.implements(IWidget)

    name = '' 
    label = u''
    description = u''
    mode = FORM_INPUT
    required = False 
    error = None 
    value = None
    setErrors = True

    form = None
    content = None
    context = None
    params = MultiDict({})
    localizer = None

    def __init__(self, node, typ):
        self.node = node
        self.typ = typ

        self.name = node.name
        self.id = node.name.replace('.', '-')
        self.label = node.title
        self.description = node.description
        self.required = node.required

    @property
    def __title__(self):
        return self.__class__.__name__

    def update(self):
        # Step 1: Determine the value.
        value = colander.null
        lookForDefault = False

        # Step 1.1: If possible, get a value from the params
        self.setErrors = False
        widget_value = self.extract()
        if widget_value is not colander.null:
            # Once we found the value in the params, it takes precendence
            # over everything and nothing else has to be done.
            self.value = widget_value
            value = PLACEHOLDER

        # Step 1.2: If we have a widget with a field and we have no value yet,
        #           we have some more possible locations to get the value
        if value is colander.null and value is not PLACEHOLDER:
            # Step 1.2.1: If the widget knows about its content and the
            #              content is to be used to extract a value, get
            #              it now via a data manager.
            if self.content is not None:
                value = getMultiAdapter(
                    (self.content, self.node), IDataManager).query()

            # Step 1.2.2: If we still do not have a value, we can always use
            #             the default value of the node, id set
            if ((value is self.node.missing or value is colander.null) and
                self.node.default is not colander.null):
                value = self.node.default
                lookForDefault = True

        # Step 1.4: Convert the value to one that the widget can understand
        if value not in (PLACEHOLDER, colander.null):
            self.value = self.node.serialize(value)
            if type(self.value) is str:
                self.value = unicode(self.value, 'utf-8')

    def extract(self, default=colander.null):
        return self.params.get(self.name, default)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)


class SequenceWidget(Widget):
    """Term based sequence widget base.

    The sequence widget is used for select items from a sequence. Don't get
    confused, this widget does support to choose one or more values from a
    sequence. The word sequence is not used for the schema field, it's used
    for the values where this widget can choose from.

    This widget base class is used for build single or sequence values based
    on a sequence which is in most use case a collection. e.g.
    IList of IChoice for sequence values or IChoice for single values.

    See also the MultiWidget for build sequence values based on none collection
    based values. e.g. IList of ITextLine
    """
    interface.implements(ISequenceWidget)

    value = ()
    terms = None
    empty_marker = ''

    noValueToken = '--NOVALUE--'

    @property
    def displayValue(self):
        value = []
        for token in self.value:
            # Ignore no value entries. They are in the request only.
            if token == self.noValueToken:
                continue
            term = self.terms.getTermByToken(token)
            if ITitledTokenizedTerm.providedBy(term):
                value.append(self.localizer.translate(term.title))
            else:
                value.append(term.value)
        return value

    def updateTerms(self):
        if self.terms is None:
            self.terms = getMultiAdapter(
                (self.content, self.node, self.node.typ, self), ITerms)
        return self.terms

    def update(self):
        self.empty_marker = '%s-empty-marker'%self.name

        # Create terms first, since we need them for the generic update.
        self.updateTerms()
        super(SequenceWidget, self).update()

    def extract(self, default=colander.null):
        if (self.name not in self.params and
            self.empty_marker in self.params):
            return default

        value = self.params.getall(self.name) or default
        if value != default:
            # do some kind of validation, at least only use existing values
            for token in value:
                if token == self.noValueToken:
                    continue
                try:
                    self.terms.getTermByToken(token)
                except LookupError:
                    return default

        if value is not default and \
                not isinstance(self.node.typ, colander.Positional):
            if value:
                return value[0]
            else:
                return default

        return value
