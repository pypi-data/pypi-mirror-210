from abc import ABC, abstractmethod
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk

from turandot.model import ConfigModel
from turandot.ui import i18n
from turandot.gtk4.presentations import LocalizedEnumDropdown

# Placeholder to implement localization later
_ = i18n


class SettingsViewBase(ABC):

    def __init__(self, label_string: str):
        self.label_string = label_string
        self.label = self._create_label()

    @abstractmethod
    def _create_label(self) -> Gtk.Label:
        pass

    @abstractmethod
    def attach(self, add_to: Gtk.Grid, row: int):
        pass


class SettingsControlBase(SettingsViewBase, ABC):

    def __init__(self, config_key: str | list, label_string: str):
        self.config = ConfigModel()
        super().__init__(label_string)
        self.config_key = config_key
        self.entry_widget = self._create_entry_widget()

    def _create_label(self) -> Gtk.Label:
        label = Gtk.Label(label=self.label_string)
        label.set_halign(Gtk.Align.START)
        return label

    @abstractmethod
    def _create_entry_widget(self) -> Gtk.Widget:
        pass

    @abstractmethod
    def _connect(self):
        pass

    def attach(self, add_to: Gtk.Grid, row: int):
        add_to.attach(self.label, 0, row, 1, 1)
        add_to.attach(self.entry_widget, 1, row, 1, 1)


class TitleControl(SettingsViewBase):

    def _create_label(self) -> Gtk.Label:
        label = Gtk.Label()
        label.set_markup(f"<b>{self.label_string}</b>")
        label.set_margin_top(15)
        label.set_halign(Gtk.Align.START)
        return label

    def attach(self, add_to: Gtk.Grid, row: int):
        add_to.attach(self.label, 0, row, 2, 1)

    def hide(self):
        self.label.hide()

    def show(self):
        self.label.show()

class TextControl(SettingsControlBase):

    def __init__(self, config_key: str | list, label_string: str):
        self.buffer = Gtk.EntryBuffer()
        super().__init__(config_key, label_string)
        self._connect()

    def _create_entry_widget(self) -> Gtk.Widget:
        entry = Gtk.Entry()
        entry.set_buffer(self.buffer)
        text_data = str(self.config.get_key(self.config_key))
        text_len = len(text_data)
        self.buffer.set_text(text_data, text_len)
        return entry

    def _connect(self):
        self.entry_widget.connect("changed", self._on_change)

    def _on_change(self, *args):
        val = self.buffer.get_text()
        self.config.set_key(self.config_key, val)


class SpinControl(SettingsControlBase):

    def _empty_callback(self, *args):
        pass

    def _create_entry_widget(self) -> Gtk.Widget:
        spinner = Gtk.SpinButton()
        spinner.set_adjustment(self.adjustment)
        spinner.set_numeric(self.integer)
        if self.integer:
            val = int(self.config.get_key(self.config_key))
        else:
            val = self.config.get_key(self.config_key)
        self.adjustment.set_value(val)
        return spinner

    def _connect(self):
        # self.entry_widget.connect("scroll-event", self._empty_callback)
        # self.entry_widget.connect("scroll", self._empty_callback)
        self.entry_widget.connect("changed", self._on_change)

    def __init__(
        self,
        config_key: str | list,
        label_string: str,
        from_: float = 0x400,
        to: float = 0xFFFF,
        inc: float = 1.0,
        integer: bool = True,
        wrap: bool = True
    ):
        self.adjustment = Gtk.Adjustment(value=0, lower=from_, upper=to, step_increment=inc)
        self.integer = integer
        super().__init__(config_key, label_string)
        self._connect()

    def _on_change(self, *args):
        if self.integer:
            val = int(self.adjustment.get_value())
        else:
            val = self.adjustment.get_value()
        self.config.set_key(self.config_key, val)


class SwitchControl(SettingsControlBase):

    def __init__(self, config_key: str | list, label_string: str):
        self.switch = Gtk.Switch()
        super().__init__(config_key, label_string)
        self._connect()

    def _create_entry_widget(self) -> Gtk.Widget:
        val = self.config.get_key(self.config_key)
        container = Gtk.Box()
        container.set_hexpand(True)
        container.set_halign(Gtk.Align.END)
        self.switch.set_state(val)
        container.append(self.switch)
        return container

    def _connect(self):
        self.switch.connect("state_set", self._on_change)

    def _on_change(self, *args):
        self.config.set_key(self.config_key, args[1])


class EnumControl(SettingsControlBase):

    def __init__(self, config_key: str | list, label_string: str, enum_model):
        self.enum_model = enum_model
        super().__init__(config_key, label_string)
        self._connect()

    def _create_entry_widget(self) -> LocalizedEnumDropdown:
        return LocalizedEnumDropdown(self.enum_model)

    def _connect(self):
        self.entry_widget.connect("changed", self._on_change)

    def _on_change(self, *args):
        enum_val = self.entry_widget.get_active_member()
        self.config.set_key(self.config_key, enum_val.value)
