# nara

A plug-in framework for **modal Python applications** — vim-like editors, keyboard-driven tools, anything where you press keys and things happen in modes.

nara gives you:

- A `Plug` base class with a standard lifecycle (`setup` → `tearup`) and auto-loaded TOML config.
- An `App` that wires seven managers together for you: plug loading, key listening, state tracking, action delegation, buffer/view management, styling, and config.
- A `@tag(...)` decorator that binds a method to a key sequence in a specific mode — like vim's `:nnoremap` but in Python.
- A `@deleg(...)` decorator that registers a method as a queryable agent other plugs can call.
- A `vimo` sub-package with `View`, `Model`, `Object`, `Item`, `Element` base classes for the MVC side.

If you've ever wanted to build "vim but for X" — nara is the scaffolding.

---

## What's in the box

```
nara/
├── plug.py              ← Plug base class — every component inherits from this
├── app/
│   ├── app.py           ← App: composes the seven managers
│   ├── plugman.py       ← discovers & loads plugs from <config>/autorun/
│   ├── earman.py        ← key listener: matches key sequences to tagged methods
│   ├── stateman.py      ← tracks current mode / view / state
│   ├── delegman.py      ← action delegation: route "goTo" / "insert" / ... to plugs
│   ├── buffman.py       ← buffer / view manager
│   ├── configman.py     ← TOML config, platform-aware paths (XDG / macOS / Windows)
│   └── styleman.py      ← styling
├── vimo/
│   ├── view.py          ← View base class
│   ├── model.py         ← Model base class
│   ├── object.py        ← Object base class
│   ├── item.py          ← Item base class
│   └── element.py       ← Element base class
└── utils/
    ├── tag/             ← @tag and @deleg decorators + key parser
    ├── dicts.py         ← dotdict (dict with attribute access)
    ├── cache.py
    ├── factory.py
    └── parser.py
```

## Requirements

- Python 3.9+
- [`tomli`](https://pypi.org/project/tomli/) 2.0 (for TOML config parsing)

## Installation

### From PyPI (when published)

```bash
pip install nara
```

### From source

```bash
git clone https://github.com/aotabekov91/nara.git
cd nara
pip install .
```

## Quick start — a one-plug app

### 1. Write a plug

Each plug lives in its own package and exposes a `get_plug_class()` factory:

```
myplug/
└── src/
    └── myplug/
        └── __init__.py
```

```python
# src/myplug/__init__.py
from nara import Plug, tag

class MyPlug(Plug):
    """Greets the world on every keypress of 'g' in normal mode."""

    prefix_keys = ["(normal)"]   # default mode prefix for this plug's commands

    def setup(self):
        super().setup()
        self.count = 0

    @tag("(normal)")
    def greet(self, view=None, xrange=[1], **kwargs):
        self.count += xrange[-1]
        print(f"hello #{self.count}")

def get_plug_class():
    return MyPlug
```

### 2. Drop it in the autorun folder

```bash
mkdir -p ~/.config/<app>/autorun
cp -r myplug ~/.config/<app>/autorun/
```

### 3. Boot the app

```python
from nara import App

class MyApp(App):
    pass

app = MyApp()
app.activate()   # loads plugs from <config>/autorun/
app.run()
```

On boot, `Plugman` walks `<config>/autorun/`, imports each plug's `src/<name>/` package, calls `get_plug_class()`, and instantiates the returned class with `app=<app>` and `config=<from config.toml>`.

## The `@tag` decorator — key bindings

`@tag("(mode)")` marks a method as a key-bound command in a specific mode. The key sequence is the method name by default; you can override it:

```python
@tag("(normal)")
def w(self, view=None, xrange=[1], **kwargs):
    """Press 'w' in normal mode → move forward one word."""
    ...

@tag("(normal)")
def save(self, view=None, **kwargs):
    """Press 's' 'a' 'v' 'e' in normal mode."""
    ...
```

### Counts and ranges

nara parses vim-style counts automatically. If the user types `3w`, the `w` method receives `xrange=[3]`. Methods that accept a count declare `xrange=[1]` in their signature:

```python
@tag("(normal)")
def d(self, view=None, xrange=[1], **kwargs):
    """'d' deletes; '3d' deletes 3 times."""
    for _ in range(xrange[-1]):
        ...
```

Multi-range counts like `2,3d` (delete 2 then 3) arrive as `xrange=[2, 3]`.

### Mode prefixes

A plug's `prefix_keys` attribute declares which mode(s) its commands belong to by default. To bind a command in multiple modes, list them:

```python
class MyPlug(Plug):
    prefix_keys = ["(normal)", "(visual)"]

    @tag("(normal)")
    def x(self, view=None, **kwargs):
        """'x' in normal mode."""
        ...

    @tag("(visual)")
    def x(self, view=None, **kwargs):
        """'x' in visual mode — different behavior."""
        ...
```

## The `@deleg` decorator — cross-plug queries

One plug often needs to ask another plug to do something (e.g. "Normal" plug → "go to line N"). `@deleg` registers a method as a queryable agent:

```python
from nara import Plug, deleg

class Normal(Plug):
    @deleg("goTo@(normal){Normal}")
    def goTo(self, view, data):
        """Other plugs can ask Normal to goTo a position."""
        view.setCursor(data)
```

Other plugs query it via `app.delegman`:

```python
self.app.delegman.delegate(
    mode="normal",
    action="goTo",
    view=view,
    data=some_position,
)
```

Or get the agent directly:

```python
agent = self.app.delegman.getAgent(
    mode="normal", view=view, action="goTo")
if agent:
    agent(view, some_position)
```

## Configuration

nara apps read their config from a TOML file at `<config_dir>/<app_name>/config.toml`. The config dir is platform-aware:

| OS | Path |
| --- | --- |
| Linux | `$XDG_CONFIG_HOME/<app>/` or `~/.config/<app>/` |
| macOS | `~/Library/Application Support/<app>/` |
| Windows | `%APPDATA%/<app>/` |
| Other (BSD) | `$XDG_CONFIG_HOME/<app>/` or `~/.config/<app>/` |

### Config file format

```toml
# config.toml

# Per-plug sections: each plug reads its own section into self.m_config
[MyPlug]
greeting = "hello"
count = 0

[MyPlug.Settings]
# Settings subsection: keys become instance attributes on the plug
verbose = true
```

Each plug also reads a `config.toml` from its own source directory (next to `__init__.py`) — those defaults are merged with the app-level config, with app-level taking precedence.

## The `Plug` lifecycle

Every nara component inherits from `Plug`. The lifecycle:

```python
class Plug:
    name: str = None           # defaults to class name
    isMode: bool = False       # True for mode plugs (Normal, Insert, ...)
    addToApp: bool = True      # auto-register with App on setup

    def __init__(self, app=None, files={}, config={}, **kwargs):
        self.app = app
        self.m_config = config
        self.m_kwargs = kwargs
        self.files = files.copy()
        self.setup()

    def setup(self):
        self.setName()         # name = class name if not set
        self.updateConf()      # merge app config into m_config
        self.setBasePath()     # self.path = dir of the source file
        self.setFiles()        # index files in self.path; load config.toml if present
        self.setSettings()     # [Settings] subsection → instance attributes
        self.updateArgs()      # [Settings] subsection → kwargs too
        self.setApp()          # register self with app, hook appConfigChanged

    def tearup(self):
        """Unregister from earman + plugman on shutdown."""
        ...
```

`setup()` runs at construction time. Override it in subclasses to add your own initialization — always call `super().setup()` first.

## The seven managers

`App.setupParts()` constructs these in order:

| Manager | Purpose |
| --- | --- |
| `Delegman` | Routes `delegate(mode, action, view, data)` calls to `@deleg`-tagged methods. |
| `Earman` | Listens to key presses, accumulates them, matches against `@tag`-bound methods, runs the match (with optional count via `xrange`). |
| `Stateman` | Tracks the active mode (`normal` / `insert` / `visual` / ...), the active view, and the current state tuple. |
| `Buffman` | Manages open views/buffers. Emits `viewCreated` when a new view opens. |
| `Plugman` | Discovers plugs in `<config>/autorun/`, imports them, instantiates them. Tracks plugs by name and by source path. |
| `Styleman` | Styling/theming. |
| `Configman` | Reads `config.toml`, exposes `config()` and `configFolder()`. |

Each manager is itself a `Plug` — they compose via `App.setupParts()` and register with each other automatically.

## The `vimo` sub-package — view MVC

For the view side, nara provides base classes in `nara.vimo`:

| Class | Role |
| --- | --- |
| `View` | A visible buffer the user interacts with. Has a manager (the buffman or a parent view). |
| `Model` | The data backing a view. |
| `Object` | A semantic object in the document (a word, a line, a node). |
| `Item` | A renderable item. |
| `Element` | The smallest renderable unit. |

These are abstract bases — subclass them to build your document model and rendering.

## Plugin discovery — what `Plugman` looks for

`Plugman.loadAutorunPlugs()` scans `<config>/autorun/`. For each subdirectory `<name>/`:

1. Adds `<name>/src/` to `sys.path`.
2. Imports the module `<name>` (so `<name>/src/<name>/__init__.py` must exist).
3. Calls `get_plug_class()` from that module.
4. Instantiates the returned class (or each class in the returned list) with `app=`, `config=` (from `config.toml`'s section for that class name).

So the canonical plug layout is:

```
<config>/autorun/<plug_name>/
├── src/
│   └── <plug_name>/
│       └── __init__.py     ← defines get_plug_class()
└── config.toml             ← optional plug-local config
```

## Example plug — a leap/jump history

A real example: [leaper](https://github.com/aotabekov91/leaper) is a nara plug that adds vim-style jump-list navigation (`Ctrl-O` / `Ctrl-I`) to any nara-based editor. Its core is:

```python
from nara import Plug, tag

class Leaper(Plug):
    prefix_keys = ["(normal)"]

    def setup(self):
        super().setup()
        self.m_leaps = {}
        # Hook into the host app's signals
        self.app.buffman.viewCreated.connect(self.saveView)
        ...

    @tag("(normal)")
    def prev(self, view=None, xrange=[1], **kwargs):
        """Leap backward in jump history."""
        ...

    @tag("(normal)")
    def next(self, view=None, xrange=[1], **kwargs):
        """Leap forward in jump history."""
        ...
```

That's the whole plug. `prev` and `next` are automatically bound to `p` `r` `e` `v` and `n` `e` `x` `t` in normal mode, with count support (`3prev` leaps back 3 jumps).

## File layout

```
nara/
├── src/nara/
│   ├── __init__.py           ← exports Plug, App, all managers, vimo, utils
│   ├── plug.py               ← Plug base class
│   ├── app/
│   │   ├── __init__.py
│   │   ├── app.py            ← App
│   │   ├── plugman.py        ← Plugman
│   │   ├── earman.py         ← Earman
│   │   ├── stateman.py       ← Stateman
│   │   ├── delegman.py       ← Delegman
│   │   ├── buffman.py        ← Buffman
│   │   ├── configman.py      ← Configman
│   │   ├── styleman.py       ← Styleman
│   │   ├── utils/
│   │   └── vimo/
│   ├── vimo/
│   │   ├── view.py
│   │   ├── model.py
│   │   ├── object.py
│   │   ├── item.py
│   │   └── element.py
│   └── utils/
│       ├── tag/              ← @tag, @deleg, key parser
│       ├── dicts.py          ← dotdict
│       ├── cache.py
│       ├── factory.py
│       └── parser.py
├── pyproject.toml            ← poetry build config
├── LICENSE
└── README.md
```

## Dependencies

```toml
[tool.poetry.dependencies]
python = "^3.9"
tomli = "==2.0"
```

That's it. nara itself has no other runtime dependencies — the Qt/UI layer is provided by the host app (e.g. PyQt6), not by nara.

## License

See [LICENSE](LICENSE).
