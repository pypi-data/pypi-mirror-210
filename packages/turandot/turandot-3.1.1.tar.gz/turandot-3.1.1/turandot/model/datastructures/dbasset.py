from abc import ABC, abstractmethod
from typing import Optional, Union
from pathlib import Path
from turandot.model.datastructures.baseasset import BaseAsset


class DatabaseAsset(BaseAsset, ABC):
    """Base class for conversion assets that are savable to and loadable from the database"""

    ZERO_VALUES = [None, "0", 0]
    TITLE_NOT_FOUND_MSG = "- title not found -"

    def __init__(self, path: Union[str, Path], dbid: Optional[int] = None, expand: bool = False):
        self.dbid = dbid
        self.title = DatabaseAsset.TITLE_NOT_FOUND_MSG
        BaseAsset.__init__(self, path=path, expand=expand)

    @abstractmethod
    def _read_title(self):
        """Read title from database asset"""
        pass

    @classmethod
    @abstractmethod
    def get(cls, dbid: int, expand: bool = False):
        """Get conversion asset by database id"""
        pass

    @classmethod
    @abstractmethod
    def get_all(cls, expand: bool = False) -> list:
        """Get list of all database assets of this specific class"""
        pass

    @abstractmethod
    def save(self):
        """Save conversion asset to database"""
        pass

    @abstractmethod
    def delete(self):
        """Delete conversion asset from the database"""
        pass
