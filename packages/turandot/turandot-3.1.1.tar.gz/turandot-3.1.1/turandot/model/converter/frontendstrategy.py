from abc import ABC, abstractmethod
from turandot.model import QueueMessage, CompanionData


class FrontendStrategy(ABC):
    """
    Interface to be implemented by the frontend
    Allows state notification from the backend
    """

    @abstractmethod
    def handle_message(self, msg: QueueMessage):
        """Handle a Queue message from the backend: Do something with it on the frontend"""
        pass

    @abstractmethod
    def handle_companion_data(self, data: CompanionData):
        """Handle a companion data object after conversion: Do something with it on the frontend"""
        pass


class PrintStrategy(FrontendStrategy):
    """Dummy implementation of frontend strategy"""

    def handle_message(self, msg: QueueMessage):
        print(msg)

    def handle_companion_data(self, data: CompanionData):
        print(data)
