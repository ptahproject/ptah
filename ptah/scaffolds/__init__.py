from textwrap import dedent

from pyramid.scaffolds.template import Template


class PtahTemplate(Template):


    def post(self, command, output_dir, vars): # pragma: no cover
        separator = "=" * 79
        msg = dedent(
            """
            %(separator)s
            Examples: https://github.com/ptahproject/examples
            Documentation: https://ptahproject.readthedocs.org

            Mailing List: https://groups.google.com/forum/#!forum/ptahproject
            Twitter: https://twitter.com/ptahproject

            Welcome to Ptah. Dorneles hopes you like it.
            %(separator)s
        """ % {'separator': separator})

        self.out(msg)
        return super(PtahTemplate, self).post(command, output_dir, vars)


class PtahStarterProjectTemplate(PtahTemplate):
    _template_dir = 'ptah_starter'
    summary = 'Ptah Starter - blank Ptah scaffold'
