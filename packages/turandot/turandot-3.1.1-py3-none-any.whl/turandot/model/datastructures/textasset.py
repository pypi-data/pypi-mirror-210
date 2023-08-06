from turandot.model.datastructures.baseasset import BaseAsset


class TextAsset(BaseAsset):
    """Base class to represent a conversion asset consisting of a single text file"""

    def expand(self):
        self._read_path()
        self._read_content()
