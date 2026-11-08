import typing as tp

from ..plug import Plug

class Buffman(Plug):

    def __init__(self, app: tp.Any) -> None:
        super().__init__(app)
        self.m_views: tp.Set[tp.Any] = set()
        self.m_viewers: tp.Dict[str, tp.Any] = {} 
        self.m_modellers: tp.Dict[str, tp.Any] = {} 
        self.m_models: tp.Dict[tp.Any, tp.Any] = {}

    def models(self) -> tp.Dict[tp.Any, tp.Any]:
        return self.m_models

    def views(self) -> tp.Set[tp.Any]:
        return self.m_views

    def setModel(self, idx: tp.Any, model: tp.Any) -> None:
        if model:
            self.m_models[idx] = model

    def createViewClass(
            self, 
            klass, 
            view_model=None, 
            **kwargs
            ) -> tp.Any:
        if klass:
            kwargs["app"] = self.app
            view=klass(**kwargs)
            if view_model is not None:
                view.setModel(model=view_model)
            self.saveView(view)
            return view

    def saveView(self, view: tp.Any) -> None:
        self.m_views.add(view)

    def removeView(self, view=None, **kwargs):
        self.m_views.discard(view)

    def locateView(self, view=None, pos = {}, **kwargs) -> tp.Any:
        if view:
            view_pos = view.position.copy()
            pos.update(view_pos)
            loc = pos.get(view.name, None)
            if loc:
                return loc, self.app.view.child(loc)
        return None, None

    def setup(self) -> None:
        super().setup()
        self.setParser()

    def addClass(self, klass, kind=None):
        if not klass in self.m_classes:
            self.m_classes+=[klass]
        if kind=='viewer':
            return self.addViewer(klass)
        elif kind=='modeller':
            return self.addModeller(klass)
        return klass

    def viewer(self, name):
        return self.m_viewers.get(name, None)

    def addViewer(self, name, klass) -> tp.Any:
        self.m_viewers[name]=klass
        return klass

    def modeller(self, name):
        return self.m_modellers.get(name, None)

    def addModeller(self, name, klass) -> tp.Any:
        self.m_modellers[name]=klass
        return klass

    def delViewer(self, name):
        return self.m_viewers.pop(name)

    def delModeller(self, name):
        return self.m_modellers.pop(name)

    def viewers(self) -> tp.List[tp.Any]:
        return self.m_viewers

    def modellers(self) -> tp.List[tp.Any]:
        return self.m_modellers

    def createModel(
        self,
        klass: tp.Callable[[...], tp.Any],
        name: tp.Any,
        source: tp.Any,
        **kwargs,
    ) -> tp.Any:
        conf = self.app.configman.config()
        spec_conf = self.getConfig(klass, conf)
        gen_conf = kwargs.get("config", {})
        gen_conf.update(spec_conf)
        kwargs["config"] = gen_conf
        model = klass(app=self.app, source=source, **kwargs)
        self.setModel(name, model)
        model.load()
        return model

    def createView(
            self,
            klass,
            model=None,
            manager=None,
            location=None,
            **kwargs,
            ) -> tp.Any:
        conf = self.app.configman.config()
        spec_conf = self.getConfig(klass, conf)
        gen_conf = kwargs.get("config", {})
        gen_conf.update(spec_conf)
        kwargs["config"] = gen_conf
        view = self.createViewClass(klass, view_model=model, **kwargs)
        view.resetConfigure(model=model, **kwargs)
        xlocation, xmanager=self.locateView(view=view, **kwargs)
        manager=manager or xmanager
        location=location or xlocation
        if manager:
            manager.addView(view=view, loc=location, **kwargs)
        return view

    def getModel(self, source: tp.Any, **kwargs) -> tp.Any:
        for name, klass in self.m_modellers.items():
            if not klass.isCompatible(source, **kwargs):
                continue
            name = klass.getSourceName(source, **kwargs)
            model = self.m_models.get(name, None)
            if not model:
                model = self.createModel(
                    klass, name, source, **kwargs)
            model.resetConfigure(source=source, **kwargs)
            return model

    def getView(self, model: tp.Any, **kwargs) -> tp.Any:
        if model.wantUniqView:
            for view in self.m_views:
                if view.model() != model:
                    continue
                view.resetConfigure(model=model, **kwargs)
                return view
        for name, klass in self.m_viewers.items():
            if klass.isCompatible(model, **kwargs):
                return self.createView(
                    klass, model, **kwargs)

    def initiate(self, source: str, **kwargs) -> tp.Any:
        model = self.getModel(source, **kwargs)
        if model:
            return self.getView(model, **kwargs)

    def open(self, source: str, **kwargs) -> tp.Any:
        view = self.initiate(source, **kwargs)
        if view:
            view.activate(**kwargs)
            view.redraw()
        return view

    def checkParser(self) -> tp.Any:
        args, unkwn = self.app.parser.parse()
        if args.source:
            self.open(source=args.source)

    def setParser(self) -> tp.Any:
        self.app.parser.addArgument(
            "source", nargs="?", default=None)

    def getConfig(
        self,
        obj: tp.Any,
        config: tp.Dict[str, tp.Any],
    ) -> tp.Dict[str, tp.Any]:
        conf = {}
        for i in obj.__mro__[::-1]:
            n = i.__name__
            conf.update(config.get(n, {}))
        conf.update(config.get(obj.name, {}))
        return conf
