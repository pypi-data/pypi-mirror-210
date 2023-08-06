from abc import ABC, abstractmethod


class BaseController(ABC):

    def __init__(self, view):
        self.view = view

    @abstractmethod
    def connect(self):
        pass
