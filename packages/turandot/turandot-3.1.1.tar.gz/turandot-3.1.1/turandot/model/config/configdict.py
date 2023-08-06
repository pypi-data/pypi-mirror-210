from abc import ABC, abstractmethod
from typing import Union, OrderedDict, Any


class ConfigDict(dict):
    """Overridden dict class with fancier getters/setters"""

    @staticmethod
    def _rec_ordered_to_dict(od: Any):
        """Convert a nested OrderedDict to ConfigDict recursively"""
        if not isinstance(od, (OrderedDict, dict)):
            return od
        for k, v in od.items():
            if isinstance(v, (OrderedDict, dict)):
                od[k] = ConfigDict._rec_ordered_to_dict(v)
        return ConfigDict(od)

    @classmethod
    def from_ordered(cls, od: Union[OrderedDict, dict]):
        """Create object from ruamel.yaml OrderedDict"""
        return cls(ConfigDict._rec_ordered_to_dict(od))

    def interlace(self, d: dict):
        """
        Override values with values from an incoming dict
        :param d: Dict containing the values to override
        :return: New ConfigDict with overridden values
        """
        interlaced = self | d
        return ConfigDict.from_ordered(interlaced)

    def get_key(self, key: Union[list, str], default=None):
        """
        Get nested key by key string or list of key strings
        :param key: key as string or list of keys for nested dicts
        :param default: default value to return if key is not found
        :return: value for key
        """
        if type(key) != list:
            return self.get(key, default)
        elif len(key) == 0:
            return self
        else:
            if key[0] not in self.keys():
                return default
            hay = self.get(key[0])
            if len(key[1:]) == 0:
                return hay
            elif isinstance(hay, ConfigDict):
                return hay.get_key(key[1:], default=default)
            return default
