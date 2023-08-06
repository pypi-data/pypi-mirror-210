from typing import Optional, Union
from pathlib import Path
from bs4 import BeautifulSoup

from turandot.model import DatabaseAsset, ConfigModel
from turandot.model.sql import Repository


class CslAsset(DatabaseAsset):
    """Conversion asset representing a CSL file"""

    def __init__(self, path: Union[Path, str], dbid: Optional[int] = None, expand: bool = False):
        DatabaseAsset.__init__(self, path=path, dbid=dbid, expand=expand)

    def expand(self):
        self._read_path()
        self._read_content()
        self._read_title()

    def _read_title(self):
        try:
            soup = BeautifulSoup(self.content, "xml")
            self.title = str(soup.style.info.title.contents[0])
        except Exception:
            self.title = CslAsset.TITLE_NOT_FOUND_MSG

    @classmethod
    def get(cls, dbid: int, expand: bool = False):
        repo = Repository()
        data = repo.get_csl(dbid=dbid)
        if data is None:
            return None
        return cls(**data, expand=expand)

    @classmethod
    def get_all(cls, expand: bool = False) -> list:
        repo = Repository()
        data = repo.get_all_csl()
        objlist = []
        for i in data:
            objlist.append(cls(**i, expand=expand))
        objlist.sort(key=lambda x: x.title.lower())
        return objlist

    def save(self):
        repo = Repository()
        self.dbid = repo.save_csl(self.dbid, self.path)

    def delete(self):
        repo = Repository()
        repo.delete_csl(self.dbid)
