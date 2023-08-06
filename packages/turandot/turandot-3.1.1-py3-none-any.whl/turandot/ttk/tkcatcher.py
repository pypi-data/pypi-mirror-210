from turandot.ui import CatcherStrategy
from turandot.ttk.controllers import ExceptionController


class TkCatcher(CatcherStrategy):
    """Tk specific exception handling strategy"""

    def __init__(self, ctrl: ExceptionController):
        self.exc_controller = ctrl

    def handle_exception(self, e: Exception, tb: str):
        """Draw exception and traceback to Tk frontend"""
        self.exc_controller.draw_exception(e, tb)
