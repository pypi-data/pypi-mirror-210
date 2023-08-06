from pathlib import Path
from typing import Optional, Union
from abc import ABC, abstractmethod
from turandot import TurandotAssetException
from turandot.model import ConfigModel


class BaseAsset(ABC):
    """
    Base class for conversion assets
    Has a path, can read from it and can save exceptions if anything goes wrong
    """

    def __init__(self, path: Union[Path, str], expand: bool = False):
        self.path: Path = Path(path)
        self.directory: Optional[Path] = None
        self.content: str = ""
        self.exception: Optional[Exception] = None
        if expand:
            try:
                self.expand()
            except Exception as e:
                self.exception = e

    @abstractmethod
    def expand(self):
        """Create complete object with asset content"""
        pass

    def _read_path(self):
        """Fill path and directory attribute, throw exception if not found"""
        if str(self.path) == "":
            raise TurandotAssetException("Asset path must not be empty".format(self.path.name))
        if not self.path.is_file():
            raise TurandotAssetException("Not a file: {}".format(self.path.name))
        self.directory = self.path.parent

    def _read_content(self):
        """Read asset file content"""
        enc = ConfigModel().get_key(["general", "encoding"], default="utf8")
        with self.path.open('r', encoding=enc) as f:
            self.content = f.read()
