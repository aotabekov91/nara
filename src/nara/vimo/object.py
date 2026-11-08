class Object:

    name = None
    kind = None

    def __init__(
            self, 
            app=None, 
            config={},
            name=None, 
            parent=None, 
            manager=None,
            attributes=[],
            objectName=None,
            appConfig=False, 
            **kwargs,
            ):

        self.app = app
        self.m_name = name
        self.m_config = config
        self.m_parent = parent
        self.m_manager = manager
        self.m_attributes=attributes
        self.m_app_config = appConfig
        self.m_objectName = objectName
        self.m_kwargs = kwargs
        self.m_custom_attrs={}
        super().__init__()
        self.setup()

    def setup(self):
        self.updateAttribute()
        self.setConf()
        self.setName()
        self.setKind()
        self.setApp()
        if self.m_manager:
            self.setManager(self.m_manager)

    def setApp(self):
        if self.app:
            self.app.addObject(self, view=True)
            if self.m_app_config:
                app_config = self.app.configman.config()
                klass_config = self.klassConfig(app_config)
                self.m_config.update(klass_config)

    def updateAttribute(self):
        for attribute in self.m_attributes:
            key=attribute.get('key')
            value=attribute.get('value')
            kind=attribute.get('kind', None)
            copy=attribute.get('copy', False)
            attr=getattr(self, key, None)
            if copy:
                value=value.copy()
            if not kind:
                setattr(self, key, value)
            elif kind=='update' and not attr is None:
                attr.update(value)
            elif kind=='append' and not attr is None:
                attr.append(value)
            else:
                raise
                #todo

    def setAttr(self, name, value, custom=False):
        if not custom:
            setattr(self, name, value)
        else:
            self.m_custom_attrs[name]=value

    def getAttr(self, name, default=None, custom=False):
        if not custom:
            return getattr(self, name, default)
        else:
            return self.m_custom_attrs.get(name, default)

    def setManager(self, manager=None):
        if self.m_manager:
            self.m_manager.betChild(self)
        self.m_manager = manager
        if self.m_manager:
            self.m_manager.setChild(self)

    def manager(self):
        return self.m_manager

    def setName(self, name=None):
        if not name:
            c = self.__class__.__name__
            c = self.m_name or c
            name = self.name or c
        self.name = name

    def setConf(self, data=None):
        data = data or self.m_config
        if not data:
            return
        for k, v in data.items():
            setattr(self, k, v)

    def klassConfig(self, config):
        conf = {}
        klass_mro=self.__class__.__mro__
        for klass in klass_mro[::-1]:
            name = klass.__name__
            conf.update(config.get(name, {}))
        conf.update(config.get(self.name, {}))
        return conf

    def config(self):
        return self.m_config

    def setProp(self, name, value=True, view=None):
        view = view or self
        setattr(view, name, value)

    def delProp(self, what):
        delattr(self, what)

    def getProp(self, what, view=None):
        view = view or self
        return getattr(view, what, None)

    def checkProp(self, what, view=None):
        view = view or self
        if type(what) != list:
            what = [what]
        for w in what:
            if not getattr(view, w, False):
                return False
        return True

    def setKind(self):
        name = self.__class__.__name__
        self.kind = self.kind or name

    def resetConfigure(self, **kwargs):
        pass

    def __bool__(self):
        return True
