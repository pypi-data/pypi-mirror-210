from abc import ABC, abstractmethod
from turandot.ttk.view import TurandotTtkView


class ControllerBase(ABC):
    """Abstract class to subclass controllers from"""

    def __init__(self, view: TurandotTtkView):
        self.view = view
