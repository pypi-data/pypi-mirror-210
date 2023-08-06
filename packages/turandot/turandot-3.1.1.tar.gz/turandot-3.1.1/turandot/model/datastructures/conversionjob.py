import uuid
import multiprocessing
from typing import Optional, Union
from dataclasses import dataclass, astuple
from pathlib import Path
from turandot.model import TemplateAsset, CslAsset, TextAsset, SourceAsset, ConfigModel, ReferenceSource, ConversionAlgorithm, ConfigDict


@dataclass
class CurrentStep:
    """Data class to contain plain text of the document during conversion"""

    filename: str = ""
    content: str = ""

    def save_file(self, directory: Path):
        """Save step result to file for debugging"""
        with Path(directory / self.filename).open("w") as f:
            f.write(self.content)


@dataclass
class JobAssets:
    """Container class for all assets: source file, template, csl file"""
    sourcefile: Union[Path, str, SourceAsset]
    template: Union[int, TemplateAsset]
    cslfile: Optional[Union[int, CslAsset]] = None
    csljson: Optional[Union[Path, str, TextAsset]] = None

    def __iter__(self):
        return iter(astuple(self))


@dataclass
class JobSettings:
    """Container class for settings from GUI"""
    conversion_algorithm: ConversionAlgorithm
    reference_source: ReferenceSource
    zotero_lib_id: Optional[int] = None


class ConversionJob:
    """Data class containing all necessary information to perform a conversion"""

    def __init__(self, job_assets: JobAssets, job_settings: JobSettings, msgqueue: multiprocessing.Queue):
        self.job_assets: JobAssets = job_assets
        self.job_settings: JobSettings = job_settings
        self.msgqueue: multiprocessing.Queue = msgqueue
        self.current_step: CurrentStep = CurrentStep()
        self.conversion_id = str(uuid.uuid4())
        self.config: ConfigDict = ConfigModel().get_dict()
