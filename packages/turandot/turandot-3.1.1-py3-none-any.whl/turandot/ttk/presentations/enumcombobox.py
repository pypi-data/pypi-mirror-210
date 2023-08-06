from typing import Optional, Callable
from enum import EnumMeta
import tkinter as tk
from tkinter import ttk

from turandot.ttk.presentations import KvCombobox


class EnumCombobox(KvCombobox):
    """Key-value combobox to return enum values on selection"""

    def __init__(self, master: tk.BaseWidget, model: EnumMeta, textdict: Optional[dict] = None, **kwargs):
        super().__init__(master, **kwargs)
        for i in model:
            if textdict is None:
                self.add_option(i, str(i.value))
            else:
                self.add_option(i, textdict.get(i, i.value))
