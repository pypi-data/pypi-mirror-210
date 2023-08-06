from enum import Enum
from md_citeproc import NotationStyle, OutputStyle

from turandot.model import ReferenceSource, ConversionAlgorithm


class EnumTranslations:
    """Human readable text for each entry of an enum dropdown"""

    textentries: dict[Enum, str] = {
        ReferenceSource.NOTHING: "No automatic processing",
        ReferenceSource.NOSOURCE: "Processing without data source",
        ReferenceSource.ZOTERO: "Zotero",
        ReferenceSource.JSON: "CSLJSON file",

        ConversionAlgorithm.WEASYPRINT: "Weasyprint/PDF",

        NotationStyle.INLINE: "inline",
        NotationStyle.FOOTNOTE: "footnotes",
        NotationStyle.INLINE_FOOTNOTE: "inline-footnotes",

        OutputStyle.INLINE: "inline",
        OutputStyle.NUM_FOOTNOTES: "enumerated footnotes"
    }

    inversion = dict((v, k) for k, v in textentries.items())

    @staticmethod
    def get(key: Enum):
        """Get human readable text"""
        return EnumTranslations.textentries.get(key, key.name)

    @staticmethod
    def inverse_get(value: str):
        """
        This is a really dumb method to do this
        but ttk's combobox widgets are kind of forcing this method
        """
        return EnumTranslations.inversion.get(value, None)
