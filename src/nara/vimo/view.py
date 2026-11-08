from .object import Object

class View(Object):

    position = {}
    prefix_keys = []
    isSubview = False
    activated = False

    def __init__(
        self,
        model=None,
        index=None,
        pindex=None,
        identifier=None,
        **kwargs,
    ):
        self.m_id = index
        self.m_pid = pindex
        self.m_children = {}
        self.m_model = model
        self.m_vid = identifier
        super().__init__(**kwargs)

    def setIdentifier(self, idx):
        self.m_vid = idx

    def identifier(self):
        return self.m_vid

    def child(self, pos, recursive=True):
        if pos.startswith("!"):
            child_view = self.m_children.get(pos[1:])
            if child_view:
                return child_view
            elif recursive:
                for i in self.m_children.values():
                    child_view = i.child(pos, recursive)
                    if child_view:
                        return child_view
        elif pos:
            pos_data = pos.split("|", 1)
            child_view = self.m_children.get(pos_data[0])
            if not child_view:
                return self
            elif len(pos_data) == 1:
                return child_view
            elif not child_view is None and recursive:
                return child_view.child(pos_data[1], recursive)

    def setChild(self, obj):
        pidx = obj.posIndex()
        idx = obj.identifier()
        if not idx is None:
            self.m_children[str(idx)] = obj
        if not pidx is None:
            self.m_children[str(pidx)] = obj

    def betChild(self, obj):
        child = None
        pidx = obj.posIndex()
        idx = obj.identifier()
        if not idx is None:
            child = self.m_children.pop(
                    str(idx), None)
        if not pidx is None:
            child = self.m_children.pop(
                    str(pidx), None)
        return child

    def updateChildIndex(self, n, o, child):
        self.m_children.pop(o, None)
        self.m_children[n] = child

    def setIndex(self, index=None):
        self.m_id = index

    def index(self):
        return self.m_id

    def posIndex(self):
        return self.m_pid

    def fullPosIndex(
        self,
        suffix="",
        recursive=True,
    ):
        pidx = self.posIndex()
        idx = self.identifier()
        c1 = not idx is None
        c2 = not pidx is None
        sep = self.m_kwargs.get(
                "suffix_separator", "|")
        sep = getattr(
                self, "suffix_separator", sep)
        if c1 and c2:
            fidx = f"{pidx}[{idx}]"
        elif idx:
            fidx = str(idx)
        else:
            fidx = str(pidx)
        if suffix:
            suffix = f"{fidx}{sep}{suffix}"
        else:
            suffix = fidx
        if recursive:
            m = self.m_manager
            if m and m != self.app.view:
                return m.fullPosIndex(
                        suffix, recursive)
        return suffix

    def setPosIndex(self, idx=None):
        self.m_pid = idx

    def model(self):
        return self.m_model

    def setModel(self, model):
        if id(self.m_model) != id(model):
            self.m_model = model
            self.kind = getattr(model, 'kind', None)

    @classmethod
    def isCompatible(cls, model, **kwargs):
        name = cls.name or cls.__name__
        wanted=getattr(model, "wantView", [])
        return name in wanted 

    def toggle(self, *args, **kwargs):
        if self.activated and self.isVisible():
            self.octivate(*args, **kwargs)
        else:
            self.activate(*args, **kwargs)

    def octivate(self, *args, restore=True, **kwargs):
        self.activated = False
        manager = self.manager()
        kwargs['view']=self
        if restore and self.app:
            self.app.stateman.betView(*args, **kwargs)
        if manager:
            manager.betView(self, *args, **kwargs)

    def activate(self, *args, recursive=False, **kwargs):
        self.activated = True
        manager = self.manager()
        kwargs['view']=self
        if manager:
            manager.setView(*args, **kwargs)
            if recursive and not manager.activated:
                manager.activate(recursive=recursive, **kwargs)
        if self.app:
            self.app.stateman.setView(*args, **kwargs)
        if self.checkProp("setFocus"):
            self.show()
            self.setFocus()

    def betView(self, *args, recursive=False, **kwargs):
        self.octivate(recursive=recursive, **kwargs)

    def addView(self, *args, view=None, **kwargs)->None:
        if view:
            view.setManager(self)
            if self.checkProp("setParent", view):
                view.setParent(self)

    def setView(self, *args, view=None, **kwargs)->None:
        if view:
            self.m_view = view
            if self.checkProp("setFocus", view):
                view.setFocus()
