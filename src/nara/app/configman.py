import os
import tomli
import platform

from ..plug import Plug

class Configman(Plug):

    def setup(self):
        super().setup()
        self.setConfigFolder()
        self.updateConfigFile()
        self.readConfigFile()
        self.app.createFolder(self.m_config_path)

    def config(self):
        return self.m_config

    def readConfigFile(self):
        config_file = self.app.files.get('config.toml', None)
        if config_file:
            with open(config_file, "rb") as y:
                self.m_config = tomli.load(y)
        else:
            self.m_config = {}

    def updateConfigFile(self):
        config_file_path = os.path.join(self.m_config_path, 'config.toml')
        if os.path.isfile(config_file_path):
            "Updating config file path if it exists in config folder"
            self.app.files['config.toml']=config_file_path

    def configFolder(self):
        return self.m_config_path

    def setConfigFolder(self) -> str:
        """Return the platform-appropriate config directory for ``app_name``."""
        system = platform.system()
        home = os.path.expanduser('~')
        app_name = self.app.__class__.__name__.lower()

        if system == 'Linux':
            base = os.environ.get('XDG_CONFIG_HOME') or os.path.join(home, '.config')
        elif system == 'Darwin':
            base = os.path.join(home, 'Library', 'Application Support')
        elif system == 'Windows':
            base = os.environ.get('APPDATA') or os.path.join(home, 'AppData', 'Roaming')
        else:
            # FreeBSD, OpenBSD, etc. — behave like XDG.
            base = os.environ.get('XDG_CONFIG_HOME') or os.path.join(home, '.config')

        self.m_config_path = os.path.join(base, app_name)
