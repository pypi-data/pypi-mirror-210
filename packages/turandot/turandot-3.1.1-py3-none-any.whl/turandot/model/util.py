import os
from pathlib import Path
from importlib import resources
from importlib.resources import files

from turandot import assets


class ModelUtils:
    """Static helper functions for the model"""

    @staticmethod
    def get_config_dir() -> Path:
        # Config path for Windows, something like C:\User\username\Appdata\Roaming
        if 'APPDATA' in os.environ:
            confighome = Path(os.environ['APPDATA']).resolve()
        # Config path for macOS
        elif 'XDG_CONFIG_HOME' in os.environ:
            confighome = Path(os.environ['XDG_CONFIG_HOME']).resolve()
        # Config path for Linux, /home/username/.config
        else:
            confighome = Path(os.environ['HOME']).resolve() / '.config'
        configpath = confighome / 'turandot'
        return configpath

    @staticmethod
    def get_config_file() -> Path:
        return ModelUtils.get_config_dir() / "config3.yaml"

    @staticmethod
    def get_asset_content(filename: str) -> str:
        return files(assets).joinpath(filename).read_text()

    @staticmethod
    def get_asset_bytes(filename: str) -> bytes:
        return files(assets).joinpath(filename).read_bytes()
