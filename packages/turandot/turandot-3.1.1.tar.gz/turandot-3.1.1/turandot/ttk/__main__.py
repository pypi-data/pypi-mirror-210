from turandot.ui import ExceptionCatcher, TurandotFrontend
from turandot.ttk.controllers import \
    SettingsController, DbDropdownController, ConverterController, ExceptionController, AboutController, \
    ExportController
from turandot.ttk.view import TurandotTtkView
from turandot.ttk import TkCatcher


class TurandotTtk(TurandotFrontend):
    """Assemble and draw TK frontend for the application"""

    def __init__(self):
        self.view = TurandotTtkView()
        # Controller needed for the exception catcher
        self.exception_controller = ExceptionController(self.view)
        catcher_strategy = TkCatcher(self.exception_controller)
        self.catcher = ExceptionCatcher()
        self.catcher.set_strategy(catcher_strategy)

    def _attach_controllers(self):
        """Attach all controllers to the view"""
        SettingsController(self.view)
        DbDropdownController(self.view)
        ConverterController(self.view)
        AboutController(self.view)
        ExportController(self.view)

    def run(self):
        """Run the TK frontend of the application"""
        self._attach_controllers()
        self.view.run()


if __name__ == "__main__":
    TurandotTtk().run()
