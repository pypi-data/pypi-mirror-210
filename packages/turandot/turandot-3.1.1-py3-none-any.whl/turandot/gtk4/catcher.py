from turandot.ui import CatcherStrategy
from turandot.gtk4 import TurandotMainWindow
from turandot.gtk4.guithread import guithread
from turandot.gtk4.dialogs import ErrorDialog


class GtkCatcher(CatcherStrategy):
    """
    Strategy to catch exceptions and show the traceback in a dialog,
    evoked by the @catch_exception decorator
    """

    def __init__(self, mainwindow: TurandotMainWindow):
        self.mainwindow = mainwindow
        self.e: Exception | None = None
        self.tb: str | None = None
        self._connect_events()

    def _connect_events(self):
        self.mainwindow.dismiss_error_button.connect("clicked", self._hide_container)
        self.mainwindow.show_error_button.connect("clicked", self._show_traceback)

    def _hide_container(self, *args):
        self.mainwindow.error_container.hide()

    def _show_traceback(self, *args):
        dialog = ErrorDialog(self.mainwindow, self.e, self.tb)
        dialog.show()

    @guithread
    def handle_exception(self, e: Exception, tb: str):
        self.e = e
        self.tb = tb
        self.mainwindow.error_container.show()
