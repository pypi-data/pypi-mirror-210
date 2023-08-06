from abc import ABC, abstractmethod
from copy import deepcopy

from turandot.ttk.presentations import NotificationReason, DatabaseDropdownObservable
from turandot.ttk.presentations import KvCombobox


class DropdownObserver(ABC):
    """Observer base class to subclass comboboxes from"""

    @abstractmethod
    def update(self, subject: DatabaseDropdownObservable, reason: NotificationReason):
        """Update observer on notification"""
        pass


class DatabaseDropdown(KvCombobox, DropdownObserver):
    """Combobox attached to a database fed observable to change options on notification without new entry option"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

    def update(self, subject: DatabaseDropdownObservable, reason: NotificationReason):
        """Update combobox option on notification"""
        prev_selected = self.get()
        self.clear()
        for i in subject.entries:
            self.add_option(i.dbid, i.title)
        if reason != NotificationReason.INIT and self.check_key(prev_selected):
            self.set(prev_selected)
        else:
            if len(self["values"]) > 0:
                self.current(0)


class DatabaseNewOptDropdown(DatabaseDropdown):
    """Combobox attached to a database fed observable to change options on notification with new entry option"""

    NEW_TEXT = "- create new entry -"

    def update(self, subject: DatabaseDropdownObservable, reason: NotificationReason):
        """Update combobox option on notification"""
        prev_selected = self.get()
        prev_entries = set(self.get_keys())
        self.clear()
        self.add_option(0, DatabaseNewOptDropdown.NEW_TEXT)
        for i in subject.entries:
            self.add_option(i.dbid, i.title)
        if reason == NotificationReason.NEW:
            new_entries = set(self.get_keys())
            diff = new_entries - prev_entries
            self.set(list(diff)[0])
        elif reason in (NotificationReason.CHANGE, NotificationReason.DELETE) and self.check_key(prev_selected):
            self.set(prev_selected)
        else:
            self.current(0)
