import os
import sys
import importlib
import typing as tp

from ..plug import Plug
from ..utils import dotdict

class Plugman(Plug):

    path_plugs={}
    plugs: tp.Dict[tp.Any, tp.Any] = dotdict()

    def loadAutorunPlugs(self, params={}):
        config_folder = self.app.configman.configFolder()
        autorun = os.path.join(config_folder, 'autorun')
        if os.path.isdir(autorun):
            aset, paths=self.getPlugs(autorun)
            self.loadKlasses(aset, paths, params)

    def loadKlasses(self, klasses, paths={}, params={}):
        for klass in klasses: 
            path=paths.get(klass, None)
            if not path in self.path_plugs:
                self.path_plugs[path]=[]
            name = klass.__name__
            plug=self.loadPlug(klass, params)
            if plug:
                self.plugs[name] = plug
                self.path_plugs[path]+=[plug]

    def isLoaded(self, plug_class):
        for plug in self.plugs.values():
            if plug.__class__ == plug_class:
                return True
        return False

    def loadPlug(self, klass, params= {}) -> bool:
        if not self.isLoaded(klass):
            name = klass.__name__
            args = params.get(name, {})
            app_config = self.app.configman.config()
            config = app_config.get(name, {})
            try:
                plug = klass(app=self.app, config=config, **args)
                return plug
            except Exception as error:
                print("Error in plug loading: ", name, error)
                raise

    def getPlugs(self, folder, modules=None):
        paths={}
        klasses=set()
        folder=str(folder)
        modules=modules or os.listdir(folder)
        for data in modules:
            try:
                mfolder=os.path.join(folder, f'{data}/src')
                sys.path.insert(0, mfolder)
                plug_path=os.path.join(folder, data)
                module = importlib.import_module(data)
                functor = getattr(module, "get_plug_class", None)
                if functor:
                    plugger = functor()
                    if type(plugger) != list:
                        plugger = [plugger]
                    for klass in plugger:
                        klasses.add(klass)
                        paths[klass]=plug_path
            except ModuleNotFoundError as error:
                msg = "Error in plug importing: "
                print(msg, data, error)
                raise
            except Exception as error:
                msg = "Error in plug importing: "
                print(msg, data, error)
                raise
        return klasses, paths

    def getPlug(self, name=None, path=None):
        if name:
            return self.plugs.get(name, None)
        elif path:
            return self.path_plugs.get(path, [])

    def delPlug(self, name=None, path=None):
        plug=self.getPlug(name=name, path=path)
        if plug:
            name=plug.__class__.__name__
            self.plugs.pop(name, None)
            pick=None
            for path, pick in self.path_plugs.items():
                if pick==plug: break
            if pick:
                self.path_plugs.pop(path, None)
