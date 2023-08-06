from typing import Callable

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from turandot.ui import catch_exception, background, i18n
# Placeholder to implement localization later
_ = i18n


class ConfirmationDialog(Gtk.Dialog):

    def __init__(self, parent: Gtk.Window, message: str, callback: Callable, callback_args: list | None = None):
        super().__init__(title=_("Confirmation"))
        self.set_transient_for(parent)
        self.callback = callback
        self.callback_args = [] if callback_args is None else callback_args
        self.content = self.get_content_area()
        self.content.set_margin_top(10)
        self.content.set_margin_start(10)
        self.content.set_margin_end(10)
        self.content.set_margin_bottom(10)
        self.content.set_spacing(15)
        lbl = Gtk.Label(label=message)
        self.content.append(lbl)
        self.cancel_button = self.add_button(button_text=_("Cancel"), response_id=Gtk.ResponseType.CANCEL)
        self.cancel_button.set_margin_bottom(10)
        self.ok_button = self.add_button(button_text=_("OK"), response_id=Gtk.ResponseType.OK)
        self.ok_button.set_margin_start(15)
        self.ok_button.set_margin_bottom(10)
        self.ok_button.set_margin_end(10)
        self.connect_events()

    def connect_events(self):
        self.cancel_button.connect("clicked", self._on_cancel)
        self.ok_button.connect("clicked", self._on_confirm)

    def _on_cancel(self, *args):
        self.destroy()

    def _on_confirm(self, *args):
        self.callback(*self.callback_args)
        self.destroy()
