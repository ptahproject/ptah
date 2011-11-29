import os
from pyramid.scaffolds.template import Template


class PtahTemplate(Template):

    def post(self, command, output_dir, vars): # pragma: no cover
        print ("\n\nPtah has generated your application. Your application "
               "can be found at /. \n\nDorneles hopes you like it.\n")

        return super(PtahTemplate, self).post(command, output_dir, vars)


class Ptah101ProjectTemplate(PtahTemplate):
    _template_dir = 'ptah101'
    summary = 'demonstrates form, limited mgmt ui'


class Ptah102ProjectTemplate(PtahTemplate):
    _template_dir = 'ptah102'
    summary = 'demonstrates form, models, limited mgmt ui'


class Ptah201ProjectTemplate(PtahTemplate):
    _template_dir = 'ptah201'
    summary = 'demonstrates form, models, limited mgmt ui and auth'


class Ptah301ProjectTemplate(PtahTemplate):
    _template_dir = 'ptah301'
    summary = 'demonstrates traversal, localroles, full mgmt ui'
