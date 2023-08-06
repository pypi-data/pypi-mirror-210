from typing import Optional, Union
from pathlib import Path
import zipfile
import yaml
import frontmatter
from yaml.scanner import ScannerError
from turandot import TurandotAssetException
from turandot.model import DatabaseAsset, ConfigModel
from turandot.model.sql import Repository


class TemplateAsset(DatabaseAsset):
    """Conversion asset representing a conversion template"""

    METAFILE: str = "meta.yaml"

    def __init__(self, path: str, allow_mako: bool, allow_jinja: bool, dbid: Optional[int] = None, expand: bool = False):
        self.allow_jinja: bool = allow_jinja
        self.allow_mako: bool = allow_mako
        self.zipped: bool = False
        self.metadata: dict = {}
        DatabaseAsset.__init__(self, path=path, dbid=dbid, expand=expand)

    def expand(self):
        self._read_path()
        self.zipped = zipfile.is_zipfile(self.path)
        self._read_meta()
        self._read_title()
        self._read_content()

    def _read_zipped_meta(self) -> dict:
        """Get metadata dict from a zipped template"""
        try:
            with zipfile.ZipFile(self.path) as f:
                yamlstr = f.read(TemplateAsset.METAFILE)
            return yaml.safe_load(yamlstr)
        except FileNotFoundError:
            raise TurandotAssetException("Metadata file not found")
        except ScannerError:
            raise TurandotAssetException("Template metadata file not readable")

    def _read_text_meta(self) -> dict:
        """Get metadata dict from a non-zipped template"""
        try:
            enc = ConfigModel().get_key(["general", "encoding"], default="utf8")
            with self.path.open('r', encoding=enc) as f:
                metatext = f.read()
            return yaml.safe_load(metatext)
        except FileNotFoundError:
            raise TurandotAssetException("Metadata file not found")
        except ScannerError:
            raise TurandotAssetException("Template metadata file not readable")

    def _read_meta(self):
        """Read metadata from template"""
        self.metadata = self._read_zipped_meta() if self.zipped else self._read_text_meta()

    def _read_title(self):
        self.title = self.metadata.get("title", TemplateAsset.TITLE_NOT_FOUND_MSG)

    def _read_content(self):
        self.content = self._read_zipped_content() if self.zipped else self._read_text_content()

    def _read_text_content(self) -> str:
        """Read template entry point content from a non-zipped template"""
        entrypoint = self.directory / self.metadata.get("entrypoint", None)
        if entrypoint is None:
            raise TurandotAssetException("No entrypoint for template specified")
        if not entrypoint.is_file():
            raise TurandotAssetException("Entrypoint file not found at {}".format(entrypoint))
        with entrypoint.open('r') as f:
            content = f.read()
        return content

    def _read_zipped_content(self) -> str:
        """Read template entry point content from a zipped template"""
        entrypoint = self.metadata.get("entrypoint", None)
        if entrypoint is None:
            raise TurandotAssetException("No entrypoint for template specified")
        try:
            with zipfile.ZipFile(self.path) as f:
                content = f.read(entrypoint)
            return content.decode()
        except FileNotFoundError:
            raise TurandotAssetException("Entrypoint file not found")

    @classmethod
    def get(cls, dbid: int, expand: bool = False):
        repo = Repository()
        data = repo.get_template(dbid=dbid)
        if data is None:
            return None
        return cls(**data, expand=expand)

    @classmethod
    def get_all(cls, expand: bool = False) -> list:
        repo = Repository()
        data = repo.get_all_templates()
        objlist = []
        for i in data:
            objlist.append(cls(**i, expand=expand))
        objlist.sort(key=lambda x: x.title.lower())
        return objlist

    def save(self):
        repo = Repository()
        self.dbid = repo.save_template(self.dbid, self.path, self.allow_jinja, self.allow_mako)

    def delete(self):
        repo = Repository()
        repo.delete_template(self.dbid)
