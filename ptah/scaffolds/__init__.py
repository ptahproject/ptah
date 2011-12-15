import os
from pyramid.scaffolds.template import Template


class PtahTemplate(Template):

    def post(self, command, output_dir, vars): # pragma: no cover
        print ("\n\nPtah has generated your application. Your application "
               "can be found at /. \n\nDorneles hopes you like it.\n")

        return super(PtahTemplate, self).post(command, output_dir, vars)


class PtahStarterProjectTemplate(PtahTemplate):
    _template_dir = 'ptah_starter'
    summary = 'Ptah Starter - blank Ptah scaffold'
