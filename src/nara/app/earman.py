import inspect
import itertools
import typing as tp

from ..plug import Plug
from ..utils import parse

class Earman(Plug):
    """The class listens to/acts on key presses"""

    wait_run: int = 5
    wait_time: int = 500
    delisten_key: tp.List[tp.Any] = []

    def setup(self):
        self.m_keys = {}
        self.m_digits = []
        self.m_leaders = {}
        self.m_objects = {}
        self.m_letters = ""
        self.m_func_objects = {}
        self.m_event_handlers={}

    def eventHandler(self, kind):
        return self.m_event_handlers.get(kind, None)

    def addEventHandler(self, kind, handler):
        self.m_event_handlers[kind]=handler

    def keys(self):
        return self.m_keys

    def objects(self):
        return self.m_objects

    def letters(self) -> str:
        return self.m_letters

    def digits(
        self, convert=False
    ) -> tp.List[str] | tp.List[int]:
        if not convert:
            return self.m_digits
        else:
            return [int(d) for d in self.m_digits]

    def add(self, obj) -> None:
        if obj:
            is_view = self.check("isView", obj)
            ldr = getattr(obj, "listen_leader", None)
            if ldr:
                self.m_leaders[ldr] = obj
            if not obj.name in self.m_objects:
                self.m_objects[obj.name] = set()
            self.m_objects[obj.name].add(obj)
            self.setObjKeys(obj, is_view)

    def sub(self, obj) -> None:
        is_view = self.check("isView", obj)
        ldr = getattr(obj, "listen_leader", None)
        if ldr:
            self.m_leaders.pop(ldr)
        objects=self.m_objects[obj.name]
        objects.discard(obj)
        self.subObjKeys(obj, is_view)

    def subObjKeys(self, obj, view):
        keys = self.getObjKeys(obj, view)
        for key, data, state in keys:
            self.m_func_objects[data].discard(obj)
            self.m_keys[state][key].discard(data)

    def setObjKeys(self, obj, view):
        keys = self.getObjKeys(obj, view)
        for key, data, state in keys:
            if not data in self.m_func_objects:
                self.m_func_objects[data] = set()
            self.m_func_objects[data].add(obj)
            if not state in self.m_keys:
                self.m_keys[state] = {}
            if not key in self.m_keys[state]:
                self.m_keys[state][key] = set()
            self.m_keys[state][key].add(data)

    def clearKeys(self) -> None:
        """Clear the earman's state"""
        self.m_digits = []
        self.m_letters = ""

    def checkKeyer(self, event) -> bool:
        """Check the app keyer"""
        keyer = self.app.stateman.keyer()
        if keyer:
            keyer(event)
            return True
        return False

    def checkLeader(self, event):
        for key, plug in self.m_leaders.items():
            if self.app.stateman.passive():
                if plug.name != self.name:
                    continue
            if (key,) in key:
                func = getattr(plug, "checkLeader", None)
                if func:
                    cond = func(key)
                    if not cond:
                        return False
                self.togglePlug(plug)
                return True
        return False

    def checkPassive(self, event) -> bool:
        if self.app.stateman.passive():
            self.clearKeys()
            return True

    def checkDelisten(self, event) -> bool:
        mode = self.app.stateman.mode()
        c1 = self.letters() in self.delisten_key
        if c1 and mode != "normal":
            self.clearKeys()
            return True
        return False

    def checkPartial(self, event) -> bool:
        c1 = len(self.m_letters) == 0
        if c1 and self.checkLeader(event):
            return True
        return False

    def checkFunctor(self, event) -> bool:
        functor = self.app.stateman.functor()
        if functor and functor(event, self):
            return True
        return False

    def getViewMRO(self, view):
        views=[]
        view_klasses=view.__class__.__mro__
        for klass in view_klasses:
            views+=[klass.__name__]
        return views[::-1]

    def checkMatch(self, event) -> bool:
        key = self.letters()
        xrange = self.digits(convert=True)
        if key:
            view=self.app.stateman.view()
            views=self.getViewMRO(view)
            state = self.app.stateman.state()
            match, partial = self.match(
                key,
                xrange,
                state,
                self.m_keys,
                self.m_objects,
                view,
                views)
            if match or partial:
                self.run(match, partial, xrange)
                return True
        else:
            if self.app.stateman.passive():
                return False
            if xrange:
                return True
            # and xrange and passive:
            # return True
        return False

    def run(self, match, partial, xrange):
        if len(match) == 1:
            self.timer.timeout.disconnect()
            func = lambda: self.execute(match, xrange)
            self.timer.timeout.connect(func)
            w = self.wait_time
            if not partial:
                w = self.wait_run
            self.timer.start(w)

    def execute(self, match=None, xrange=None):
        if not match or len(match) > 1:
            return
        m = list(match)
        f = m[0]
        self.runBefore(f)
        if xrange:
            f(xrange=xrange)
        else:
            f()
        self.runAfter()

    def runAfter(self) -> None:
        self.clearKeys()

    def runBefore(self, f) -> None:
        pass

    def parseEvent(self, event):
        if hasattr(event, 'text'):
            return event.text()

    def updatePressedKey(self, event):
        text = self.parseEvent(event)
        if not text:
            return False
        elif text.isnumeric():
            if not self.m_digits:
                self.m_digits += [text]
            else:
                self.m_digits[-1] = self.m_digits[-1] + text
        elif text == "," and self.m_digits:
            self.m_digits += [""]
        else:
            self.m_letters += text
        return True

    def handleEvent(self, widget, event) -> bool:
        if self.updatePressedKey(event):
            pressed = self.letters()
            if self.checkKeyer(event):
                return True
            elif self.checkPartial(pressed):
                return True
            elif self.checkFunctor(pressed):
                return True
            # elif self.checkDelisten(pressed):
            #   return True
            elif self.checkMatch(pressed):
                return True
            elif self.checkPassive(pressed):
                return False
            self.clearKeys()
        return False

    @classmethod
    def getObjKeys(
        cls,
        obj: tp.Any,
        view: bool = False,
    ) -> tp.List[tp.Any]:
        alist = []
        oname = obj.name
        funcs = cls.getObjFuncs(obj)
        pref = cls.getObjPrefixes(obj)
        for fname, func in funcs:
            alist += cls.getFuncTags(func, oname, pref)
        return alist

    @classmethod
    def getObjPrefixes(cls, obj: tp.Any) -> tp.Dict[tp.Tuple[str], str]:
        opref = []
        for i in obj.__class__.__mro__:
            pkey = getattr(i, "prefix_keys", [])
            for j in pkey:
                if not j in opref:
                    opref.append(j)
        obj_pref = getattr(obj, "prefix_keys", [])
        if obj_pref:
            opref += obj_pref
        mpref = {}
        for tag in opref:
            parsed_tag = parse.parse_tag(tag)
            for key, mdata, vdata, _ in parsed_tag:
                mmode, smode = mdata
                mview, sview = vdata
                state = (mmode, smode, mview, sview)
                mpref[state] = key
        return mpref

    @classmethod
    def getFuncTags(cls, func, obj_name, pref = {}):
        tags = []
        key = getattr(func, "key", "")
        ptags = parse.parse_tag(key)
        data = (obj_name, func.__name__)
        for tag in ptags:
            key, mdata, vdata, _ = tag
            mmode, smode = mdata
            mview, sview = vdata
            if mview == "^":
                mview = obj_name
            state = (mmode, smode, mview, sview)
            if key.startswith("~"):
                key = key[1:]
            else:
                key_pref = pref.get(state, "")
                key = f"{key_pref}{key}"
            tags += [(key, data, state)]
        return tags

    @classmethod
    def getObjFuncs(
        cls,
        obj: tp.Any,
    ) -> tp.List[tp.Tuple[str, tp.Any]]:
        funcs = []
        for fname in obj.__dir__():
            try:
                func = obj.getAttr(fname)
            except:
                func = getattr(obj, fname, None)
            if not func:
                continue
            tagged = getattr(func, "hasTaggedKey", None)
            if tagged:
                funcs += [(fname, func)]
        return funcs

    @classmethod
    def getParentManagers(cls, obj: tp.Any, parent_managers=[]) -> tp.List[str]:
        manager=obj.manager()
        if not manager:
            return parent_managers
        parent_managers+=[manager.name]
        return cls.getParentManagers(manager, parent_managers)

    @classmethod
    def getStateKeys(cls, state, keys, views=[]):
        state_keys = {}
        modes = ["any", state[0]]
        submodes = ["any", state[1]]
        views.insert(0, "any")
        views.append(state[2])
        subviews = ["any", state[3]]
        states=[]
        for superstate in itertools.product(
            modes, submodes, views, subviews
        ):
            if not superstate in states:
                states.append(superstate)
                super_keys = keys.get(superstate, {})
                state_keys.update(super_keys)
        return state_keys

    @classmethod
    def match(cls, key, xrange, state, keys, objects, view, views):
        state_keys = cls.getStateKeys(state, keys, views)
        match, current, partial = set(), set(), set()
        for skey, data in state_keys.items():
            if key != skey[: len(key)]:
                continue
            for oname, fname in data:
                objs = objects[oname]
                for obj in objs:
                    func = getattr(obj, fname, None)
                    if not func:
                        continue
                    prm = inspect.signature(func).parameters
                    xrange_arg = prm.get("xrange", None)
                    # TODO: The following lines are commented out to fix a bug
                    # It is not clear whether this revomal causes side effects!!!
                    # if xrange and not xrange_arg:
                    #     continue
                    # elif not xrange and xrange_arg:
                    #     if xrange_arg.default==None:
                    #         continue
                    if key == skey:
                        match.add(func)
                        tmp_view=view
                        while not tmp_view is None:
                            if tmp_view==obj:
                                current.add(func)
                                break
                            elif current:
                                break
                            tmp_view=tmp_view.manager()
                    else:
                        partial.add(func)
        return current or match, partial
