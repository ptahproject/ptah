# widgets
from text import TextWidget
from file import FileWidget
from radio import RadioWidget, HorizontalRadioWidget
from tinymce import TinymceWidget
from textarea import TextAreaWidget
from password import PasswordWidget
from select import SelectWidget, MultiSelectWidget

import colander
from memphis.form import registerDefaultWidget

registerDefaultWidget(colander.Str, 'text')
registerDefaultWidget(colander.Int, 'text')
registerDefaultWidget(colander.Float, 'text')
registerDefaultWidget(colander.Date, 'date')
registerDefaultWidget(colander.DateTime, 'datetime')
registerDefaultWidget(colander.Bool, 'radio-horizontal')
