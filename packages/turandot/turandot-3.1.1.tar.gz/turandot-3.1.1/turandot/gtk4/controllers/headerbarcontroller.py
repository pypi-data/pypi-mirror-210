import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from turandot.gtk4.views import THeaderBar
from turandot.gtk4.controllers import BaseController
from turandot.gtk4.dialogs import AboutDialog, SettingsDialog


class HeaderBarController(BaseController):

    def __init__(self, view: THeaderBar, mainwindow: Gtk.Window):
        self.mainwindow = mainwindow
        super().__init__(view)
        self.connect()

    def _draw_about(self, *args):
        dialog = AboutDialog(self.mainwindow)
        dialog.show()

    def  _draw_settings(self, *args):
        dialog = SettingsDialog(self.mainwindow)
        dialog.show()

    def connect(self):
        self.view.about_button.connect("clicked", self._draw_about)
        self.view.settings_button.connect("clicked", self._draw_settings)
