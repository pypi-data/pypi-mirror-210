from tkinter import *
from tkinter import ttk

from turandot.ttk.view import ViewComponent


class AboutTab(ViewComponent):
    """View component for 'About' tab"""

    def _create_about_frame(self, aframe: ttk.Frame):
        self.widgets["about_container"] = ttk.Frame(aframe)
        self.widgets["about_container"].grid(row=0, column=0, sticky=(W, E, S, N))

    def create(self, add_to: ttk.Frame) -> ttk.Frame:
        aframe = ttk.Frame(add_to)
        aframe.grid(column=0, row=0, sticky=(N, E, S, W))
        self._create_about_frame(aframe)
        return aframe
