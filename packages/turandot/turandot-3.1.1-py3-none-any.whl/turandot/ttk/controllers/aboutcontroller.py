from tkinter import *
from tkhtmlview import HTMLLabel, HTMLScrolledText

from turandot.model import ModelUtils
from turandot.ui import FrontendUtils
from turandot.ttk.controllers import ControllerBase
from turandot.ttk.view import TurandotTtkView, TTKStyles


class AboutController(ControllerBase):
    """Controller to draw text to the 'about' tab"""

    def __init__(self, view: TurandotTtkView):
        super().__init__(view)
        style_obj = TTKStyles()
        self.font_size = style_obj.get_default_font_size()
        txt = self._prepare_markup(ModelUtils.get_asset_content("about.txt"))
        add_to = self.view.widgets["about_container"]
        htlabel = HTMLLabel(add_to, width=60, height=30)
        htlabel.grid(column=0, row=0, sticky=(W, E, N, S))
        htlabel.set_html(txt)

    def _prepare_markup(self, txt: str) -> str:
        """Add markup to text to fix text size"""
        txt = FrontendUtils.replace_version_number(txt)
        lines = txt.splitlines(keepends=False)
        markup_lines = [self._add_size(i) for i in lines if i != ""]
        return "".join(markup_lines)

    def _add_size(self, line: str) -> str:
        """Add p tags and set font sizes"""
        return '<p style="font-size:{}px;">{}</p>'.format(self.font_size, line)
