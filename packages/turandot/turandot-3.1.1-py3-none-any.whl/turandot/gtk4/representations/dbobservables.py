from typing import Type

from turandot.model import DatabaseAsset, CslAsset, TemplateAsset
from turandot.gtk4.representations import DataObservable


class DatabaseObservable(DataObservable):

    @property
    def MODEL(self) -> Type[DatabaseAsset]:
        raise NotImplementedError

    def __init__(self):
        super().__init__()
        self.entries: list[DatabaseAsset] = self.MODEL.get_all(expand=True)

    def notify(self):
        self.entries = self.MODEL.get_all(expand=True)
        super().notify()


class CslObservable(DatabaseObservable):
    MODEL = CslAsset


class TemplateObservable(DatabaseObservable):
    MODEL = TemplateAsset
