import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from turandot.ui import i18n

# Placeholder to implement localization later
_ = i18n


class ErrorDialog(Gtk.Dialog):

    def __init__(self, parent: Gtk.Window, e: Exception, tb: str):
        self.e = e
        self.tb = tb
        super().__init__()
        self.set_transient_for(parent)
        self.set_title(_("An error occurred"))
        self.set_default_size(width=600, height=500)
        self.content = self.get_content_area()
        self.content.set_orientation(Gtk.Orientation.VERTICAL)
        self.content.set_margin_top(10)
        self.content.set_margin_start(10)
        self.content.set_margin_end(10)
        self.content.set_margin_bottom(10)
        self.content.set_spacing(15)
        error_type = Gtk.Label(label=_("Error type:") + f" {type(e).__name__}")
        error_type.set_halign(Gtk.Align.START)
        self.content.append(error_type)
        err_msg = str(e)
        if len(err_msg) > 0:
            error_message = Gtk.Label(label=_("Error message:" + f"\n{str(e)}"))
            error_message.set_wrap(True)
            error_message.set_halign(Gtk.Align.START)
            self.content.append(error_message)
        tb_buffer = Gtk.TextBuffer()
        tb_buffer.set_text(tb)
        tb_view = Gtk.TextView()
        tb_view.set_buffer(tb_buffer)
        tb_view.set_monospace(True)
        tb_view.set_vexpand(True)
        tb_view.set_hexpand(True)
        tb_view.set_editable(False)
        tb_scroller = Gtk.ScrolledWindow()
        tb_scroller.set_child(tb_view)
        self.content.append(tb_scroller)
