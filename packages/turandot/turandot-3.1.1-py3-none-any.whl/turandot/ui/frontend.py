from abc import ABC, abstractmethod


class TurandotFrontend(ABC):
    """Abstract class for a GUI for the application"""

    @abstractmethod
    def run(self):
        """Draw frontend, run application"""
        pass
