import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from turandot.model import TemplateAsset
from turandot.ui import i18n

# Placeholder to implement localization later
_ = i18n


class TemplateEditorDialog(Gtk.Dialog):

    def __init__(self, parent: Gtk.Window, template: TemplateAsset | None):
        if template is None:
            super().__init__(title=_("Add template"))
        else:
            super().__init__(title=_("Edit template"))
        self.set_transient_for(parent)
        main_grid = Gtk.Grid(row_spacing=10, column_spacing=10)
        main_grid.set_margin_top(10)
        main_grid.set_margin_start(10)
        main_grid.set_margin_end(10)
        main_grid.set_margin_bottom(10)
        main_grid.set_hexpand(True)

        tf_label = Gtk.Label(label=_("Template file:"))
        main_grid.attach(tf_label, 0, 0, 1, 1)
        self.content = self.get_content_area()
        self.content.append(main_grid)
