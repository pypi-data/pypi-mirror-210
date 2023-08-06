from enum import Enum
from pathlib import Path
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio

from turandot.model.sql import Repository
from turandot.gtk4.filefilters import FileFilterList, FileFilters
from turandot.ui import i18n
# Placeholder to implement localization later
_ = i18n


class FileEntryDbKeys(Enum):
    """Primary keys to save last used file path to the db"""
    SourceFileEntry = "source_file"
    JsonSourceFile = "json_source_file"
    TemplateBaseFile = "tmpl_base_file"
    CslBaseFile = "csl_base_file"


class FileChooserDialog:
    """Draw db fed file chooser dialogs with adequate file filters and callbacks"""

    @staticmethod
    def _draw(
            parent: Gtk.Window,
            return_entry: Gtk.Entry,
            db_key: FileEntryDbKeys,
            init_path: Path | None = None,
            type_filter: FileFilterList = FileFilterList.ALL,
            title: str = _("Choose a file")
    ):
        """Draw a file chooser dialog, push path to corresponding entry if not canceled"""
        dialog = Gtk.FileChooserNative(action=Gtk.FileChooserAction.OPEN)
        FileFilters.apply(type_filter, dialog)
        dialog.set_transient_for(parent)
        dialog.set_title(title)
        if init_path is not None:
            dialog.set_current_folder(Gio.File.new_for_path(str(init_path)))
        dialog.connect("response", FileChooserDialog._selection_callback, dialog, return_entry, db_key)
        dialog.show()
        return True

    def _selection_callback(
            self,
            return_code: Gtk.ResponseType,
            dialog: Gtk.FileChooserNative,
            return_entry: Gtk.Entry,
            db_key: FileEntryDbKeys
    ):
        """Callback on ACCEPTED action: Write filename to entry and db"""
        if return_code == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            filename = file.get_path()
            return_entry.set_text(filename)
            repo = Repository()
            repo.set_file_select_persist(db_key.value, Path(filename).parent)
        dialog.destroy()

    @staticmethod
    def draw_db_fed(
            parent: Gtk.Window,
            return_entry: Gtk.Entry,
            db_key: FileEntryDbKeys,
            type_filter: FileFilterList = FileFilterList.ALL,
            title: str = _("Choose a file")
    ):
        """Show file chooser dialog, open recently used directory by loading it from the db"""
        repo = Repository()
        path = repo.get_file_select_persist(db_key.value)
        FileChooserDialog._draw(
            parent=parent,
            return_entry=return_entry,
            db_key=db_key,
            init_path=Path(path),
            type_filter=type_filter,
            title=title
        )
