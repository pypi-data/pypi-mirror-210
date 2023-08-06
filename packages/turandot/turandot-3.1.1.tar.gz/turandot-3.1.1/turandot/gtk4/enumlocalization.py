from enum import Enum
from md_citeproc import NotationStyle, OutputStyle

from turandot.ui import i18n
from turandot.model import ReferenceSource, ConversionAlgorithm, MessageType

_ = i18n


class GuiConversionState(Enum):
    IDLE = 0
    CONVERTING = 1


EnumLoc = {
    ReferenceSource.NOTHING: _("No automatic processing"),
    ReferenceSource.NOSOURCE: _("Processing without data source"),
    ReferenceSource.ZOTERO: _("Zotero"),
    ReferenceSource.JSON: _("CSLJSON file"),

    ConversionAlgorithm.WEASYPRINT: _("Weasyprint/PDF"),

    NotationStyle.INLINE: _("inline"),
    NotationStyle.FOOTNOTE: _("footnotes"),
    NotationStyle.INLINE_FOOTNOTE: _("inline-footnotes"),

    OutputStyle.INLINE: _("inline"),
    OutputStyle.NUM_FOOTNOTES: _("enumerated footnotes"),

    MessageType.EXCEPTION: _("ERROR"),
    MessageType.SUCCESS: _("Done"),
    MessageType.CANCELED: _("Canceled"),

    GuiConversionState.IDLE: _("idle"),
    GuiConversionState.CONVERTING: _("converting...")
}
