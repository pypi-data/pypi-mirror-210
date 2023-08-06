import ruamel
from io import StringIO
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from turandot.model import TemplateAsset
from turandot.ui import catch_exception, background, i18n
from turandot.gtk4.filefilters import FileFilterList
from turandot.gtk4.dialogs import FileEntryDbKeys, FileChooserDialog, ConfirmationDialog
from turandot.gtk4.views import TemplateTab
from turandot.gtk4.controllers import BaseController

# Placeholder to implement localization later
_ = i18n


class TemplateController(BaseController):

    def __init__(self, view: TemplateTab, parent: Gtk.Window):
        super().__init__(view)
        self.parent = parent
        self.connect()

    def connect(self):
        self.view.tf_select_button.connect("clicked", self._on_select_base_file)
        self.view.template_list.connect("cursor-changed", self._on_template_selected)
        self.view.new_button.connect("clicked", self._on_new_button)
        self.view.delete_button.connect("clicked", self._on_delete)
        self.view.save_button.connect("clicked", self._on_save)

    def _edit_template(self, *args):
        tmpl = self.view.template_list.get_selected_asset()
        print(tmpl.__dict__)

    def _on_select_base_file(self, *args):
        FileChooserDialog.draw_db_fed(
            parent=self.parent,
            return_entry=self.view.tf_entry,
            db_key=FileEntryDbKeys.TemplateBaseFile,
            type_filter=FileFilterList.TEMPLATES,
            title=_("Select template base file")
        )

    def _on_template_selected(self, *args):
        asset: TemplateAsset | None = self.view.template_list.get_selected_asset()
        if asset is None:
            self.view.form_title.set_markup("<b>" + _("Add template") + "</b>")
            self.view.tf_entry.set_text("")
            self.view.jinja_switch.set_active(False)
            self.view.mako_switch.set_active(False)
            self.view.metadata_buf.set_text("")
            self.view.delete_button.set_sensitive(False)
        else:
            self.view.form_title.set_markup("<b>" + _("Edit template") + "</b>")
            self.view.tf_entry.set_text(str(asset.path))
            self.view.jinja_switch.set_active(asset.allow_jinja)
            self.view.mako_switch.set_active(asset.allow_mako)
            yaml = ruamel.yaml.YAML(typ="rt", pure=True)
            yamlbuffer = StringIO()
            yaml.dump(data=asset.metadata, stream=yamlbuffer)
            self.view.metadata_buf.set_text(yamlbuffer.getvalue())
            self.view.delete_button.set_sensitive(True)

    def _on_new_button(self, *args):
        self.view.template_list.set_cursor(0)

    def _on_delete(self, *args):
        asset = self.view.template_list.get_selected_asset()
        if asset is not None:
            dialog = ConfirmationDialog(
                parent=self.parent,
                message=_("Remove template from list?\nNo files will be deleted"),
                callback=self.confirm_delete,
                callback_args=[asset]
            )
            dialog.show()

    def confirm_delete(self, asset: TemplateAsset):
        asset.delete()
        self.view.template_observable.notify()

    @background
    @catch_exception
    def _on_save(self, *args):
        asset = self.view.template_list.get_selected_asset()
        if asset is None:
            asset = TemplateAsset(
                path=self.view.tf_entry.get_text(),
                allow_jinja=self.view.jinja_switch.get_active(),
                allow_mako=self.view.mako_switch.get_active()
            )
        else:
            asset.path = self.view.tf_entry.get_text()
            asset.allow_jinja = self.view.jinja_switch.get_active()
            asset.allow_mako = self.view.mako_switch.get_active()
        asset.save()
        self.view.template_observable.notify()
