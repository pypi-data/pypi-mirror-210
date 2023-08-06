from types import SimpleNamespace
from tkinter import *
from tkinter import ttk
from tkinter.font import Font


class TTKStyles:
    """Utility class to attach styles to TTK widgets"""

    def __init__(self):
        lbl = Label(None)  # dummy button from which to extract default font
        self.font_dict = (Font(font=lbl['font'])).actual()  # get settings dict

    def add_styles(self, add_to: Tk):
        self._create_label_styles(add_to)

    def _create_label_styles(self, add_to: Tk):
        h2 = ttk.Style(add_to)
        h2.configure("h2.TLabel", font=(self.font_dict["family"], self.font_dict["size"], "bold"))
        html = ttk.Style(add_to)
        html.configure("html.Text", font=(self.font_dict["family"], self.font_dict["size"], "italic"))

    @staticmethod
    def get_padding() -> SimpleNamespace:
        p = SimpleNamespace()
        p.notebook_frames = "0 5 8 10"
        p.no_title_notebook_frames = "0 15 8 10"
        p.about_notebook_frame = "8 15 8 10"
        p.h2_top = "8 10 0 5"
        p.h2 = "8 20 0 5"
        p.left_labels = {"padx": 8, "pady": 5}
        p.right_entries = {"padx": 0, "pady": 5}
        p.inline_buttons = {"padx": 8, "pady": 20}
        p.right_most_inline_button = {"padx": 0, "pady": 20}
        p.full_process_container = {"padx": 8, "pady": 5}
        return p

    def get_default_font_size(self):
        return self.font_dict["size"]
