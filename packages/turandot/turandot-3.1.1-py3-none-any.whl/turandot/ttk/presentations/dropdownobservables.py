from abc import ABC, abstractmethod
from enum import Enum
from typing import Type

from turandot.model import DatabaseAsset, TemplateAsset, CslAsset

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from turandot.ttk.presentations import DropdownObserver


class NotificationReason(Enum):
    """Enum to describe why the observer notifies the observable"""
    INIT = 0
    NEW = 1
    CHANGE = 2
    DELETE = 3


class DropdownObservable(ABC):
    """Base class for an observable to attach to a dropdown"""

    def __init__(self):
        self.observers: list["DropdownObserver"] = []

    def attach(self, observer: "DropdownObserver"):
        """Append an observer to the observable"""
        self.observers.append(observer)

    @abstractmethod
    def notify(self, reason: NotificationReason):
        """Notify the observers"""
        pass


class DatabaseDropdownObservable(DropdownObservable, ABC):
    """DB fed observable to attach comboboxes as observers to"""

    @abstractmethod
    def get_model(self) -> Type[DatabaseAsset]:
        """Return database model the observable manages"""
        pass

    def __init__(self):
        super(DatabaseDropdownObservable, self).__init__()
        self.entries: list[DatabaseAsset] = self._get_from_db()

    def _get_from_db(self) -> list[DatabaseAsset]:
        """Get entries from database to draw to dropdown"""
        model = self.get_model()
        entrylist = model.get_all(expand=True)
        entrylist.sort(key=lambda x: x.title.lower())
        return entrylist

    def notify(self, reason: NotificationReason):
        self.entries = self._get_from_db()
        for i in self.observers:
            i.update(self, reason=reason)


class TemplateObservable(DatabaseDropdownObservable):

    def get_model(self) -> Type[DatabaseAsset]:
        return TemplateAsset


class CslObservable(DatabaseDropdownObservable):

    def get_model(self) -> Type[DatabaseAsset]:
        return CslAsset
