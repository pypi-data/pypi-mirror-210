from typing import Union, Optional
from abc import abstractmethod, ABC
from enum import EnumMeta
from tkinter import *
from tkinter import ttk

from turandot.model import ConfigModel
from turandot.ui import background, EnumTranslations
from turandot.ttk.view.styles import TTKStyles
from turandot.ttk.presentations import EnumCombobox


class SettingsViewBase(ABC):
    """Base class for all settings presentations"""

    def __init__(self, label: str, add_to: ttk.Frame, row: int):
        self.label = label
        self.add_to = add_to
        self.row = row

    @abstractmethod
    def _create_label(self) -> ttk.Label:
        """Draw label for settings presentation"""
        pass


class SettingsControlBase(SettingsViewBase, ABC):
    """Base class for writeable settings presentations"""

    def __init__(self, label: str, config_key: Union[str, list], add_to: ttk.Frame, row: int):
        super().__init__(label, add_to, row)
        self.config_key = config_key

    def _create_label(self):
        lbl = ttk.Label(self.add_to, text=self.label)
        lbl.grid(row=self.row, column=0, sticky=W, **TTKStyles.get_padding().left_labels)

    @abstractmethod
    def _callback(self):
        """The presentations callback on a change event"""
        pass


class TitleControl(SettingsViewBase):
    """Read-only presentation to draw a title"""

    def __init__(self, label: str, add_to: ttk.Frame, row: int):
        super().__init__(label=label, add_to=add_to, row=row)
        self._create_label()

    def _create_label(self):
        lbl = ttk.Label(self.add_to, text=self.label, style="h2.TLabel", padding=TTKStyles.get_padding().h2)
        lbl.grid(row=self.row, columnspan=2, sticky=(W, E))


class TextControl(SettingsControlBase):
    """Presentation to write a string to an entry widget"""

    def __init__(self, label: str, config_key: Union[str, list], add_to: ttk.Frame, row: int):
        super().__init__(label, config_key, add_to, row)
        self.entry: Optional[ttk.Entry] = None
        self.sv = StringVar(value=ConfigModel().get_key(self.config_key))
        self._create_label()
        self._create_entry()

    def _create_entry(self):
        """Draw entry widget"""
        self.entry = ttk.Entry(
            self.add_to,
            textvariable=self.sv,
        )
        self.sv.trace_add("write", self._callback)
        self.entry.grid(row=self.row, column=1, sticky=(W, E), **TTKStyles.get_padding().right_entries)

    @background
    def _callback(self, *args):
        ConfigModel().set_key(self.config_key, self.sv.get())


class SpinControl(SettingsControlBase):
    """Presentation to write a number to a spinner widget"""

    def __init__(
        self,
        label: str,
        config_key: Union[str, list],
        add_to: ttk.Frame,
        row: int,
        from_: float = 0x400,
        to: float = 0xFFFF,
        inc: float = 1.0,
        format_: str = "%1.0f",
        wrap: bool = True
    ):
        super().__init__(label, config_key, add_to, row)
        self.spinbox: Optional[ttk.Spinbox] = None
        self.iv = IntVar(value=ConfigModel().get_key(self.config_key))
        self._create_label()
        self._create_spinbox(from_, to, inc, format_, wrap)

    def _unbind_wheel(self):
        """Prevent mouse wheel from doing anything"""
        self.spinbox.unbind_class("TSpinbox", "<ButtonPress-4>")
        self.spinbox.unbind_class("TSpinbox", "<ButtonPress-5>")
        self.spinbox.unbind_class("TSpinbox", "<MouseWheel>")

    def _create_spinbox(self, from_: float, to: float, inc: float, format_: str, wrap: bool):
        """Create spinbox widget"""
        self.spinbox = ttk.Spinbox(
            self.add_to, from_=from_, to=to, increment=inc, format=format_, wrap=wrap, textvariable=self.iv
        )
        self.iv.trace_add("write", self._callback)
        self._unbind_wheel()
        self.spinbox.grid(row=self.row, column=1, sticky=(W, E), **TTKStyles.get_padding().right_entries)

    @background
    def _callback(self, *args):
        ConfigModel().set_key(self.config_key, self.iv.get())


class SwitchControl(SettingsControlBase):
    """Presentation to write a boolean value to a switch"""

    def __init__(self, label: str, config_key: Union[str, list], add_to: ttk.Frame, row: int):
        super().__init__(label, config_key, add_to, row)
        self.bv = BooleanVar(value=ConfigModel().get_key(self.config_key))
        self.checkbutton: Optional[ttk.Checkbutton] = None
        self._create_label()
        self._create_checkbutton()

    def _create_checkbutton(self):
        """Create switch widget"""
        self.checkbutton = ttk.Checkbutton(self.add_to, text="", variable=self.bv)
        self.bv.trace_add("write", self._callback)
        self.checkbutton.grid(row=self.row, column=1, sticky=E, **TTKStyles.get_padding().right_entries)

    @background
    def _callback(self, *args):
        ConfigModel().set_key(self.config_key, self.bv.get())


class TextEnumControl(SettingsControlBase):
    """Create combobox based on the values of en enum"""

    def __init__(self, label: str, config_key: Union[list, str], add_to: ttk.Frame, row: int, model: EnumMeta):
        self.model = model
        super().__init__(label, config_key, add_to, row)
        self.combobox = self._create_combobox(model)
        init_enum_val: model = self.model(ConfigModel().get_key(self.config_key, default=""))
        self.combobox.set(init_enum_val)
        self.combobox.set_callback(self._callback)
        self._create_label()

    def _create_combobox(self, model: EnumMeta) -> EnumCombobox:
        """Draw combobox"""
        combo = EnumCombobox(self.add_to, model, textdict=EnumTranslations.textentries, state="readonly")
        combo.grid(row=self.row, column=1, sticky=(W, E), **TTKStyles.get_padding().right_entries)
        return combo

    @background
    def _callback(self, *args):
        ConfigModel().set_key(self.config_key, self.combobox.get().value)
