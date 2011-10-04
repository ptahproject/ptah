"""Widget Framework Implementation"""


class HTMLFormElement(object):

    id = None
    klass = None
    title = None

    lang = None

    disabled = None
    tabindex = None
    onfocus = None
    onblur = None
    onchange = None

    def addClass(self, klass):
        """See interfaces.IHTMLFormElement"""
        if not self.klass:
            self.klass = klass
        else:
            #make sure items are not repeated
            if klass not in self.klass:
                self.klass = u'%s %s'%(self.klass, klass)

    def update(self):
        super(HTMLFormElement, self).update()
        if self.required:
            self.addClass('required')


class HTMLInputWidget(HTMLFormElement):

    readonly = None
    alt = None
    accesskey = None


class HTMLTextInputWidget(HTMLInputWidget):

    size = None
    maxlength = None


class HTMLTextAreaWidget(HTMLFormElement):

    rows = None
    cols = None
    readonly = None
    accesskey = None


class HTMLSelectWidget(HTMLFormElement):

    multiple = None
    size = 1
