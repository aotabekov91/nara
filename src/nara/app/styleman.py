import os
import re
import collections
import typing as tp

from ..plug import Plug
from ..utils import tag, deleg

class Styleman(Plug):

    current: str = None

    def setup(self):
        super().setup()
        self.m_styles={}
        self.m_style = "default"

    def cssToDict(self, css) -> tp.Dict[str, str]:
        settings = {}
        css = css.strip()
        css = re.sub(r"[\n\t]", " ", css)
        css = re.sub("}", "}__::__", css)
        pattern = r"([^{]*){([^}]*)}"
        tmp = css.split("__::__")
        for text in tmp:
            if not text:
                continue
            text = text.strip()
            m = re.match(pattern, text)
            if m:
                name = m.group(1).strip()
                inside = m.group(2).strip()
                m = {}
                for i in inside.split(";"):
                    if i:
                        i = i.strip()
                        j = i.split(":", 1)
                        m[j[0].strip()] = j[1].strip()
                settings[name] = m
        return settings

    def dictToCSS(
        self,
        style: tp.Dict[str, str],
    ) -> str:
        parts = []
        for k, v in style.items():
            inside = []
            for i, j in v.items():
                inside += [f" {i}: {j}"]
            inside = "; ".join(inside) + "; }"
            parts += [k + " {" + f" {inside} "]
        css = " ".join(parts)
        return css

    def updateDefault(self) -> None:
        self.setDefault(self.app.plugman.plugs)
        self.colorscheme(self.m_style)

    def updateColorscheme(self, css: str) -> tp.Dict[str, str]:
        data, css = self.m_styles.get("default")
        tmp = data.copy()
        return self.updateStyle(tmp, css)

    def updateStyle(self, base, append) -> tp.Dict[str, str]:
        for key, value in append.items():
            data = base.pop(key, {})
            data.update(value)
            base[key] = data
        return base

    def setDefault(self, plugs):
        default = collections.OrderedDict()
        style={}
        for plug in plugs.values():
            file = plug.files.get("style.css", None)
            if file:
                style = self.read(file)
                self.updateStyle(default, style)
        file = self.app.files.get("style.css", None)
        if file:
            style = self.read(file)
            self.updateStyle(default, style)
        css = self.dictToCSS(default)
        self.m_styles["default"] = (default, css)

    def read(
        self,
        path: str,
    ) -> tp.Union[None, tp.Dict[str, str]]:
        if not os.path.exists(path):
            return
        with open(path, "r") as y:
            lines = " ".join(y.readlines())
            css = re.sub(r"[\n\t]", " ", lines)
            return self.cssToDict(css)

    def addColorscheme(
        self, name: str, css: str, update: bool = True
    ) -> None:
        if update:
            css = self.updateColorscheme(css)
        css = self.dictToCSS(css)
        self.m_styles[name] = (css, css)
        self.reloadColorscheme()

    def reloadColorscheme(self) -> None:
        if self.current != self.m_style:
            self.colorscheme(self.m_style)

    def currentStyle(self):
        return self.current or self.m_style

    def styles(self):
        return self.m_styles

    def style(self, style=None):
        style=style or self.currentStyle() 
        return self.m_styles.get(style, None)

    @tag("(exec)", filler={"colorscheme": "colorscheme"})
    def colorscheme(self, colorscheme='default') -> None:
        self.current = None
        style = self.m_styles.get(colorscheme, None)
        default = self.m_styles.get("default", None)
        if style:
            data, css = style
            self.current = self.m_style = colorscheme
            if default:
                _, dcss = default
                css = dcss + css
            self.app.qapp.setStyleSheet(css)
        elif default:
            _, css = default
            self.app.qapp.setStyleSheet(css)
            self.current = "default"

    @deleg("colorscheme@(exec[colorscheme])")
    def colorschemes(self):
        return list(self.m_styles.keys())
