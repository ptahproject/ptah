""" Source code view """
import os.path
import pkg_resources
from ptah import view
from pyramid.httpexceptions import HTTPFound

from manage import PtahManageRoute


class SourceView(view.View):
    view.pview(
        'source.html', PtahManageRoute,
        template = view.template('ptah.manage:templates/source.pt'))

    __doc__ = 'Source introspection page.'
    __intr_path__ = '/ptah-manage/source.html'

    source = None
    format = None

    def update(self):
        name = self.request.params.get('pkg')
        if name is None:
            raise HTTPFound(location='.')

        dist = None
        pkg_name = name
        while 1:
            try:
                dist = pkg_resources.get_distribution(pkg_name)
                if dist is not None:
                    break
            except pkg_resources.DistributionNotFound:
                if '.' not in pkg_name:
                    break
                pkg_name = pkg_name.rsplit('.',1)[0]

        if dist is None:
            self.source = None

        names = name[len(pkg_name)+1:].split('.')
        path = '%s.py'%os.path.join(*names)
        try:
            abspath = pkg_resources.resource_filename(pkg_name, path)
        except:
            raise HTTPFound(location='.')

        if os.path.isfile(abspath):
            self.file = abspath
            self.name = '%s.py'%names[-1]
            self.pkg_name = pkg_name
            source = open(abspath, 'rb').read()

            if not self.format:
                from pygments import highlight
                from pygments.lexers import PythonLexer
                from pygments.formatters import HtmlFormatter

                html = HtmlFormatter(
                    linenos='inline',
                    lineanchors='sl',
                    anchorlinenos=True,
                    noclasses = True,
                    cssclass="ptah-source")

                def format(self, code, highlight=highlight,
                           lexer = PythonLexer()):
                    return highlight(code, lexer, html)

                self.__class__.format = format

            self.source = self.format(source)
