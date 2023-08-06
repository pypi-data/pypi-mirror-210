class ImportBlocker(object):
    def __init__(self, *args):
        self.module_names = args

    def find_module(self, fullname, path=None):
        if fullname in self.module_names:
            return self
        return None

    def exec_module(self, mdl):
        # return an empty namespace
        return {}
