import ptah, os, os.path
from zope import interface
from pyramid.httpexceptions import HTTPFound
from memphis import config, view
from memphis.view import tmpl
from memphis.view.customize import TEMPLATE


class TemplatesModule(ptah.PtahModule):
    """ Templates management module. """

    title = 'Templates'
    ptah.manageModule('templates')


view.registerPagelet(
    'ptah-module-actions', TemplatesModule,
    template = view.template(
        'ptah.modules:templates/customize-actions.pt', nolayer = True))


class TemplatesManagement(view.View):
    """List templates"""
    view.pyramidView(
        context = TemplatesModule,
        template = view.template(
            'ptah.modules:templates/customize.pt', nolayer=True))

    __intr_path__ = '/ptah-module/templates/index.html'

    pkg_data = None

    def update(self):
        items = tmpl.registry.items()
        items.sort()

        self.packages = [name for name, data in items]
        self.packages.sort()

        request = self.request

        self.selected = request.params.get('pkg')
        if self.selected in self.packages:
            self.pkg_data = self.load(self.selected)

    def load(self, pkg):
        data = tmpl.registry[pkg]

        templates = data.items()
        templates.sort()
        info = []
        for filename, (path,title,desc,_tmpl,pkg_name) in templates:
            info.append((filename, path))

        return info


class ViewTemplate(view.View):
    """View template"""
    view.pyramidView(
        'view.html', TemplatesModule,
        template = view.template(
            'ptah.modules:templates/template.pt', nolayer=True))

    __intr_path__ = '/ptah-module/templates/view.html'

    format = None

    def update(self):
        reg = tmpl.registry
        request = self.request

        items = tmpl.registry.items()
        items.sort()
        self.packages = [name for name, data in items]
        self.packages.sort()

        self.pkg = request.params.get('pkg')
        if self.pkg not in reg:
            raise HTTPFound(location = 'index.html')

        data = reg[self.pkg]

        self.template = request.params.get('template')
        if self.template not in data:
            raise HTTPFound(location = 'index.html')

        if 'customize' in request.POST:
            dir = TEMPLATE.custom
            if not dir:
                self.message("Customization is not allowed", 'warning')
            else:
                dest = os.path.join(dir, self.pkg)
                if not os.path.exists(dest):
                    os.makedirs(dest)

                custfile = os.path.join(dest, self.template)
                if os.path.exists(custfile):
                    self.message("Template is customized alread. Remove previous version and try again.", 'warning')
                else:
                    d = open(custfile, 'wb')
                    s = open(data[self.template][0], 'rb')
                    d.write(s.read())
                    d.close()
                    s.close()
                    raise HTTPFound(
                        location='customized.html?pkg=%s&template=%s'%(
                            self.pkg, self.template))

        if not self.format:
            from pygments import highlight
            from pygments.lexers import HtmlLexer
            from pygments.formatters import HtmlFormatter

            html = HtmlFormatter(
                linenos='inline',
                lineanchors='sl',
                anchorlinenos=True,
                noclasses = True,
                cssclass="ptah-source")

            def format(self, code, html=html,
                       highlight=highlight,
                       lexer = HtmlLexer()):
                return highlight(code, lexer, html)

            self.__class__.format = format

        text = open(data[self.template][0], 'rb').read()

        if data[self.template][0].endswith('.pt'):
            text = self.format(text)

        if isinstance(text, str):
            text = unicode(text, 'utf-8')

        self.text = text


class CustomTemplate(view.View):
    """List customized templates"""
    view.pyramidView(
        'customized.html', TemplatesModule,
        template = view.template(
            'ptah.modules:templates/customized.pt', nolayer=True))

    __intr_path__ = '/ptah-module/templates/customized.html'

    pkg = None
    template = None
    text = None
    templates = None

    def update(self):
        dir = TEMPLATE.custom

        if not dir:
            self.message("There are no any customizations", 'warning')
            raise HTTPFound(location='index.html')

        packages = []
        for name in os.listdir(dir):
            if name in tmpl.registry and \
                    os.path.isdir(os.path.join(dir, name)):
                packages.append(name)

        packages.sort()
        self.packages = packages

        reg = tmpl.registry

        pkg = self.request.params.get('pkg')
        if pkg in reg:
            self.pkg = pkg

            template = self.request.params.get('template')
            if template in reg[pkg]:
                custfile = os.path.join(dir, pkg, template)

                self.template = template

                if 'save' in self.request.POST:
                    f = open(custfile, 'wb')
                    f.write(self.request.POST['text'].encode('utf-8'))
                    f.close()
                    self.message('Template has been saved.')

                if 'remove' in self.request.POST:
                    os.unlink(custfile)
                    raise HTTPFound(location='customized.html?pkg=%s'%pkg)

                self.text = unicode(open(custfile, 'rb').read(), 'utf-8')
            else:
                data = reg[pkg]
                pkgdir = os.path.join(dir, pkg)

                templates = []
                for name in os.listdir(pkgdir):
                    if name in data:
                        templates.append((name, data[name]))

                templates.sort()
                self.templates = templates
