""" """

class FormatImpl(dict):

    def __setitem__(self, name, formatter):
        if name in self:
            raise ValueError('Formatter "%s" arelady redirected.'%name)

        super(FormatImpl, self).__setitem__(name, formatter)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


format = FormatImpl()
