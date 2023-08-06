import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from turandot.gtk4 import TurandotMainWindow
from turandot.ui import TurandotFrontend, ExceptionCatcher
from turandot.gtk4.catcher import GtkCatcher


class TurandotApplication(Gtk.Application):

    def __init__(self, **kwargs):
        self.window: Gtk.ApplicationWindow | None = None
        self.catcher: ExceptionCatcher | None = None
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, application: Gtk.Application):
        self.window = TurandotMainWindow(application=application)
        concrete_catcher = GtkCatcher(self.window)
        self.catcher = ExceptionCatcher()
        self.catcher.set_strategy(concrete_catcher)
        self.window.present()


class TurandotGtk(TurandotFrontend):

    def __init__(self):
        self.app = TurandotApplication()

    def run(self):
        self.app.run(None)


if __name__ == "__main__":
    app = TurandotGtk()
    app.run()
