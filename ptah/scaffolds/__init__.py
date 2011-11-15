import os
from paste.script.templates import Template
from paste.util.template import paste_script_template_renderer


class PtahTemplate(Template):

    def pre(self, command, output_dir, vars):
        vars['random_string'] = os.urandom(20).encode('hex')
        package_logger = vars['package']
        if package_logger == 'root':
            # Rename the app logger in the rare case a project is named 'root'
            package_logger = 'app'
        vars['package_logger'] = package_logger
        return Template.pre(self, command, output_dir, vars)

    def post(self, command, output_dir, vars):
        deo_trib = ("\n\nPtah has generated your application. Your application "
               "can be found at /. \n\nDorneles hopes you like it.\n")
        self.out(deo_trib)
        return Template.post(self, command, output_dir, vars)

    def out(self, msg): # pragma: no cover (replaceable testing hook)
        print msg


class Ptah101ProjectTemplate(PtahTemplate):
    _template_dir = 'ptah101'
    summary = 'demonstrates form, limited mgmt ui'
    template_renderer = staticmethod(paste_script_template_renderer)


class Ptah102ProjectTemplate(PtahTemplate):
    _template_dir = 'ptah102'
    summary = 'demonstrates form, models, limited mgmt ui'
    template_renderer = staticmethod(paste_script_template_renderer)


class Ptah301ProjectTemplate(PtahTemplate):
    _template_dir = 'ptah301'
    summary = 'demonstrates traversal, localroles, full mgmt ui'
    template_renderer = staticmethod(paste_script_template_renderer)
