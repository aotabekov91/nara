class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class hashdict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))
