import os
import sys
import time
import pathlib
import typing as tp

from .earman import Earman
from .plugman import Plugman
from .buffman import Buffman
from .styleman import Styleman
from .stateman import Stateman
from .delegman import Delegman
from .configman import Configman

from ..plug import Plug
from ..utils import Parser

class App(Plug):
    """The main application construct"""

    running=False
    ui: tp.Any = None
    wants_to_wait: int=0
    canHide: bool = False

    def setup(self) -> None:
        """Setting up the components of the application"""
        super().setup()
        self.setupApp()

    def setupApp(self):
        self.setupParser()
        self.setupParts()

    def setupParts(
            self, 
            delegman=Delegman,
            plugman=Plugman, 
            earman=Earman, 
            buffman=Buffman, 
            styleman=Styleman, 
            stateman=Stateman, 
            configman=Configman,
            ) -> None:
         self.delegman: Delegman = delegman(app=self)
         self.earman: Earman = earman(app=self)
         self.stateman: Stateman = stateman(app=self)
         self.buffman: Buffman = buffman(app=self)
         self.plugman: Plugman = plugman(app=self)
         self.styleman: Styleman = styleman(app=self)
         self.configman: Configman = configman(app=self)
         self.addObject(self)

    def addObject(self, obj, view=False):
        self.earman.add(obj)
        self.delegman.add(obj)
        if view:
            self.buffman.addView(obj)

    def setupParser(self, parser=Parser):
        if parser:
            self.parser: tp.Any = parser()

    def activate(self, *args, **kwargs):
        self.plugman.loadAutorunPlugs(*args, **kwargs)
        if self.ui:
            self.ui.show()

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

    def wait(self, delta: int=1) -> None:
         self.wants_to_wait += delta

    def startView(self):
         time.sleep(0.1)
         while self.wants_to_wait:
             time.sleep(0.01)
         if self.ui:
             self.ui.activate()

    def run(self) -> None:
         self.startView()
         self.running=True
         sys.exit(self.qapp.exec())

    def standardEvent(self, event):
         return event
