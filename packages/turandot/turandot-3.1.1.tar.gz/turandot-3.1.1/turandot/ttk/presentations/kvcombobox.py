from typing import Any, Callable
from bidict import bidict
from tkinter import ttk
import tkinter as tk


class KvCombobox(ttk.Combobox):
    """Key-value combobox to return something else than strings"""

    def __init__(self, master, **kwargs):
        kwargs["values"] = ()
        kwargs.pop("textvariable", None)
        self._sv = tk.StringVar()
        super(KvCombobox, self).__init__(master=master, textvariable=self._sv, **kwargs)
        self._lookup = bidict({})
        self._optstrings = []

    def clear(self):
        """Remove all options from the combobox"""
        self._lookup = bidict({})
        self._optstrings = []
        self["values"] = ()

    def _unique_option(self, option: str) -> str:
        """Create a new unique value for a given key"""
        while option in self._optstrings:
            option = f"{option}*"
        return option

    def add_option(self, key: Any, stringval: str):
        """Add new key-value pair to combobox"""
        unique_string = self._unique_option(stringval)
        self._optstrings.append(unique_string)
        self._lookup[key] = unique_string
        vallist = []
        for i in self._lookup.values():
            vallist.append(i)
        self["values"] = vallist

    def get(self) -> Any:
        """Get selected key from combobox"""
        textval = self._sv.get()
        return self._lookup.inverse.get(textval)

    def set(self, key: Any):
        """Set selected key"""
        textval = self._lookup.get(key)
        self._sv.set(textval)

    def set_callback(self, f: Callable):
        """Attach callback function to combobox"""
        self._sv.trace_add("write", f)

    def check_key(self, key: int) -> bool:
        """Check if key is in combobox"""
        return key in self._lookup.keys()

    def get_keys(self) -> list:
        """Return list of keys present in the combobox"""
        return list(self._lookup.keys())
