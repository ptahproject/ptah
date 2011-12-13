import os
from pyramid.scaffolds.template import Template


class PtahTemplate(Template):

    def post(self, command, output_dir, vars): # pragma: no cover
        print ("\n\nPtah has generated your application. Your application "
               "can be found at /. \n\nDorneles hopes you like it.\n")

        return super(PtahTemplate, self).post(command, output_dir, vars)


class Ptah001ProjectTemplate(PtahTemplate):
    _template_dir = 'ptah001'
    summary = 'Ptah001 - blank Ptah scaffold'

class Ptah101ProjectTemplate(PtahTemplate):
    _template_dir = 'ptah101'
    summary = 'Ptah101 - demonstrates form, limited mgmt ui'

class Ptah102ProjectTemplate(PtahTemplate):
    _template_dir = 'ptah102'
    summary = 'Ptah102 - demonstrates form, models, limited mgmt ui'
