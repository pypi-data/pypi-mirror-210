from enum import Enum
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from turandot.ui import i18n
# Placeholder to implement localization later
_ = i18n


class FileFilterList(Enum):
    """Enumeration of different file type filters"""
    ALL = "all"
    MARKDOWN = "markdown"
    CSL = "csl"
    JSON = "json"
    HTML = "html"
    TEMPLATES = "templates"


class FileFilters:

    @staticmethod
    def apply(filetype: FileFilterList, dialog: Gtk.FileChooserDialog):
        match filetype:
            case FileFilterList.ALL:
                dialog.add_filter(FileFilters._all())
            case FileFilterList.MARKDOWN:
                dialog.add_filter(FileFilters._markdown())
                dialog.add_filter(FileFilters._all())
            case FileFilterList.CSL:
                dialog.add_filter(FileFilters._csl())
                dialog.add_filter(FileFilters._all())
            case FileFilterList.JSON:
                dialog.add_filter(FileFilters._json())
                dialog.add_filter(FileFilters._all())
            case FileFilterList.HTML:
                dialog.add_filter(FileFilters._html())
                dialog.add_filter(FileFilters._all())
            case FileFilterList.TEMPLATES:
                dialog.add_filter(FileFilters._tmpl())
                dialog.add_filter(FileFilters._all())

    @staticmethod
    def _all() -> Gtk.FileFilter:
        """Create all files filter"""
        ff = Gtk.FileFilter()
        ff.set_name(_("All files"))
        ff.add_pattern("*")
        return ff

    @staticmethod
    def _markdown() -> Gtk.FileFilter:
        """Create markdown file filter"""
        ff = Gtk.FileFilter()
        ff.set_name(_("Markdown files"))
        ff.add_pattern("*.markdown")
        ff.add_pattern("*.mdown")
        ff.add_pattern("*.mkdn")
        ff.add_pattern("*.mkd")
        ff.add_pattern("*.md")
        ff.add_pattern("*.txt")
        return ff

    @staticmethod
    def _csl() -> Gtk.FileFilter:
        """Create csl file filter"""
        ff = Gtk.FileFilter()
        ff.set_name(_("CSL files"))
        ff.add_pattern("*.csl")
        ff.add_pattern("*.xml")
        return ff

    @staticmethod
    def _json() -> Gtk.FileFilter:
        """Create json file filter"""
        ff = Gtk.FileFilter()
        ff.set_name(_("JSON files"))
        ff.add_pattern("*.csljson")
        ff.add_pattern("*.json")
        return ff

    @staticmethod
    def _html() -> Gtk.FileFilter:
        """Create html file filter"""
        ff = Gtk.FileFilter()
        ff.set_name(_("HTML files"))
        ff.add_pattern("*.html")
        ff.add_pattern("*.htm")
        ff.add_pattern("*.xml")
        return ff

    @staticmethod
    def _tmpl() -> Gtk.FileFilter:
        """Create template file filter"""
        ff = Gtk.FileFilter()
        ff.set_name("Template files")
        ff.add_pattern("*.tmpl")
        ff.add_pattern("*.zip")
        ff.add_pattern("*.yaml")
        return ff
