from abc import ABC, abstractmethod
from tkinter import *
from tkinter import ttk


class ViewComponent(ABC):
    """Base class from view components"""

    def __init__(self):
        self.widgets = {}

    @abstractmethod
    def create(self, add_to: ttk.Frame) -> ttk.Frame:
        """Create and add the components widgets to the view"""
        pass
