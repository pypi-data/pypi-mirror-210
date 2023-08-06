from pathlib import Path
from typing import Union
import frontmatter
from turandot.model import TextAsset, ConfigModel


class SourceAsset(TextAsset):
    """Conversion asset representing the Markdown source file"""

    def __init__(self, path: Union[Path, str], expand: bool = False):
        self.metadata = {}
        TextAsset.__init__(self, path=path, expand=expand)

    def _read_content(self):
        enc = ConfigModel().get_key(["general", "encoding"], default="utf8")
        with self.path.open('r', encoding=enc) as f:
            data = frontmatter.load(f)
        self.content = data.content
        self.metadata = data.metadata
