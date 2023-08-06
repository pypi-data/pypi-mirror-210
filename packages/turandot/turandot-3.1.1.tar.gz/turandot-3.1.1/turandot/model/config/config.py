from turandot import Singleton
from pathlib import Path
from copy import deepcopy
from typing import Union, Any
import ruamel.yaml
from turandot.model import ConfigDict, ModelUtils


class ConfigModel(metaclass=Singleton):
    """Interact with Config file: Write and read config values"""

    @staticmethod
    def _initialize_default(target: Path):
        """If no config file present, init the default"""
        ModelUtils.get_config_dir().mkdir(exist_ok=True)
        with target.open('w') as fh:
            fh.write(ModelUtils.get_asset_content("default.yaml"))

    def __init__(self):
        self.yaml = ruamel.yaml.YAML(typ="rt", pure=True)
        self.path = ModelUtils.get_config_file()
        if not self.path.is_file():
            ConfigModel._initialize_default(self.path)
        self.data = self.yaml.load(self.path)

    def get_key(self, key: Union[list, str], default=None):
        """
        Get config key from file
        :param key: Key string or list of key for a nested value
        :param default: default to return if key is not found
        :return: config value
        """
        if type(key) != list:
            return self.data.get(key, default)
        else:
            search_space = self.data
            for i in key:
                if i in search_space.keys():
                    search_space = search_space.get(i)
                else:
                    return default
            return search_space

    def set_key(self, key: Union[list, str], val: Any):
        """
        Set config key in config file
        :param key: Key string or list of key for a nested value
        :param val: Value to set
        :return: None
        """
        if type(key) == str:
            self.data[key] = val
        else:
            search_space = self.data
            for i in key[:-1]:
                search_space = search_space.get(i)
            search_space[key[-1]] = val
        self.yaml.dump(self.data, self.path)

    def get_dict(self) -> ConfigDict:
        """
        Get a copy of the complete config dict (editing the copy does not edit the config!)
        :return: Deep copy of the complete config
        """
        return ConfigDict.from_ordered(deepcopy(self.data))
