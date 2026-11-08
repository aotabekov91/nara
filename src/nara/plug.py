import os
import tomli
import pathlib
import typing as tp
from inspect import getfile

class Plug:

    name: str = None
    isMode: bool = False
    shortname: str = None
    activated: bool = False
    addToApp: bool=True

    def __init__(
        self,
        app: tp.Any = None,
        files: tp.Dict[str, str] = {},
        config: tp.Dict[str, tp.Any] = {},
        functions: tp.Dict[str, tp.Any] = {},
        actions: tp.Dict[tp.Tuple[str, str], tp.Any] = {},
        **kwargs,
    ) -> None:
        super().__init__()
        self.app = app
        self.files = files.copy()
        self.functions = functions
        self.actions = actions
        self.m_config = config
        self.m_kwargs = kwargs
        self.setup()

    def setup(self) -> None:
        self.setName()
        self.updateConf()
        self.setBasePath()
        self.setFiles()
        self.setSettings()
        self.updateArgs()
        self.setApp()

    def setApp(self):
        if self.app:
            if self.addToApp:
                self.app.addObject(self)
            if self.check('appConfigChanged', self.app):
                self.app.appConfigChanged.connect(self.updateConf)

    def tearup(self) -> None:
        if self.app and self.check('earman', self.app):
            self.app.earman.sub(self)
        if self.app and self.check('plugman', self.app):
            name=self.__class__.__name__
            self.app.plugman.delPlug(name=name)

    def setName(self) -> None:
        if self.name is None:
            c = self.__class__
            self.name = c.__name__

    def updateConf(self) -> None:
        if self.app:
            if hasattr(self.app, 'configman'):
                app_config = self.app.configman.config()
                config = app_config.get(self.name, {})
                self.m_config.update(config)

    def updateArgs(self) -> None:
        setting = self.m_config.get("Settings", {})
        for key, value in setting.items():
            key_word = self.m_kwargs.get(key, {})
            if type(value) == dict:
                key_word.update(value)
                setting[key] = key_word
        self.m_kwargs.update(setting)

    def setBasePath(self) -> None:
        file = getfile(self.__class__)
        abs_path = os.path.abspath(file)
        path = os.path.dirname(abs_path)
        self.path = path.replace("\\", "/")

    def getFile(self, name):
        return self.files.get(name, None)

    def setFiles(self) -> None:
        for file in os.listdir(self.path):
            path = f"{self.path}/{file}"
            self.files[file] = path
            if file == "config.toml":
                with open(path, "rb") as y:
                    config = tomli.load(y)
                    config.update(self.m_config)
                    self.m_config = config

    def setSettings(self) -> None:
        setting = self.m_config.get("Settings", {})
        for key, value in setting.items():
            setattr(self, key, value)

    def check(self, prop, obj=None) -> bool:
        if type(prop) != list:
            prop = [prop]
        for p in prop:
            attr = getattr(obj, p, False)
            if not attr:
                return False
        return True

    def createFolder(
        self,
        path: str = None,
        parents: bool = True,
        exist_ok: bool = True,
    ) -> pathlib.Path:
        path = path or f"~/{self.name.lower()}"
        f = os.path.expanduser(path)
        path = pathlib.Path(f)
        if not os.path.exists(f):
            path.mkdir(parents=parents, exist_ok=exist_ok)
        return path

    def activate(self, *args, **kwargs):
        self.activated=True

    def octivate(self, *args, **kwargs):
        self.activated=False

    def toggle(self, *args, **kwargs):
        if self.activated:
            self.octivate(*args, **kwargs)
        else:
            self.activate(*args, **kwargs)
