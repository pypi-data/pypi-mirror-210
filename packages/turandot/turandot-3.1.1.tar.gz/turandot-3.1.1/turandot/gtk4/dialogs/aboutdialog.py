import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from turandot.model import ModelUtils
from turandot.ui import FrontendUtils
from turandot.ui import i18n

# Placeholder to implement localization later
_ = i18n


class AboutDialog(Gtk.Dialog):

    def __init__(self, parent: Gtk.Window):
        super().__init__()
        self.set_transient_for(parent)
        self.set_default_size(width=450, height=400)
        self.set_title(_("About"))
        about_label = Gtk.Label()
        about_label.set_wrap(True)
        about_label.set_vexpand(True)
        about_label.set_valign(Gtk.Align.START)
        self._draw_text(about_label)
        self.content = self.get_content_area()
        self.content.set_margin_top(10)
        self.content.set_margin_start(10)
        self.content.set_margin_end(10)
        self.content.set_margin_bottom(10)
        self.content.append(about_label)
        # self.close_button = Gtk.Button(label=_("Close"))
        # self.close_button.set_margin_top(20)
        # self.close_button.set_halign(Gtk.Align.END)
        # self.content.append(self.close_button)
        self._connect()

    @staticmethod
    def _draw_text(label: Gtk.Label):
        txt = ModelUtils.get_asset_content("about.txt")
        txt = FrontendUtils.replace_version_number(txt)
        label.set_markup(txt)

    def _close_dialog(self, *args):
        self.close()

    def _connect(self):
        # self.close_button.connect("clicked", self._close_dialog)
        pass
