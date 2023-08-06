import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from turandot.model import CslAsset
from turandot.ui import catch_exception, background, i18n
from turandot.gtk4.filefilters import FileFilterList
from turandot.gtk4.views import CslTab
from turandot.gtk4.controllers import BaseController
from turandot.gtk4.dialogs import FileEntryDbKeys, FileChooserDialog, ConfirmationDialog

# Placeholder to implement localization later
_ = i18n


class CslController(BaseController):

    def __init__(self, view: CslTab, parent: Gtk.Window):
        self.parent = parent
        super().__init__(view)
        self.connect()

    def connect(self):
        self.view.tf_select_button.connect("clicked", self._on_select_base_file)
        self.view.csl_list.connect("cursor-changed", self._on_csl_selected)
        self.view.new_button.connect("clicked", self._on_new_button)
        self.view.delete_button.connect("clicked", self._on_delete)
        self.view.save_button.connect("clicked", self._on_save)

    def _on_select_base_file(self, *args):
        FileChooserDialog.draw_db_fed(
            parent=self.parent,
            return_entry=self.view.tf_entry,
            db_key=FileEntryDbKeys.CslBaseFile,
            type_filter=FileFilterList.CSL,
            title=_("Select csl file")
        )

    def _on_csl_selected(self, *args):
        asset: CslAsset | None = self.view.csl_list.get_selected_asset()
        if asset is None:
            self.view.form_title.set_markup("<b>" + _("Add CSL file") + "</b>")
            self.view.tf_entry.set_text("")
            self.view.metadata_buf.set_text("")
            self.view.delete_button.set_sensitive(False)
        else:
            self.view.form_title.set_markup("<b>" + _("Edit CSL entry") + "</b>")
            self.view.tf_entry.set_text(str(asset.path))
            self.view.metadata_buf.set_text(f"title: {asset.title}")
            self.view.delete_button.set_sensitive(True)

    def _on_new_button(self, *args):
        self.view.csl_list.set_cursor(0)

    def _on_delete(self, *args):
        asset = self.view.csl_list.get_selected_asset()
        if asset is not None:
            dialog = ConfirmationDialog(
                parent=self.parent,
                message=_("Remove csl file from list?\nNo files will be deleted"),
                callback=self.confirm_delete,
                callback_args=[asset]
            )
            dialog.show()

    def confirm_delete(self, asset: CslAsset):
        asset.delete()
        self.view.csl_observable.notify()

    @background
    @catch_exception
    def _on_save(self, *args):
        asset = self.view.csl_list.get_selected_asset()
        if asset is None:
            asset = CslAsset(
                path=self.view.tf_entry.get_text(),
            )
        else:
            asset.path = self.view.tf_entry.get_text()
        asset.save()
        self.view.csl_observable.notify()
