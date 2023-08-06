from tkinter import messagebox
from turandot.ttk.controllers import ControllerBase


class ExceptionController(ControllerBase):
    """Controller to draw an exception onto the frontend"""

    def draw_exception(self, e: Exception, tb: str):
        """Draw exception onto the frontend"""
        exceptionstring = str(e)
        errortype = str(type(e).__name__)
        messagebox.showerror(title="Error occurred", message=exceptionstring)
        self.view.widgets["error_text_view"].delete(1.0, "end")
        self.view.widgets["error_text_view"].insert(1.0, f"{exceptionstring}\n\n{tb}")
        self.view.widgets["error_type_label_value"].set(errortype)
        self.view.widgets["error_text_view"].grid()
        self.view.widgets["error_type_desc_label"].grid()
        self.view.widgets["error_type_label"].grid()
        self.view.widgets["error_title"].grid()
