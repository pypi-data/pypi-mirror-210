from enum import Enum, EnumMeta
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk

from turandot.gtk4 import EnumLoc


class LocalizedEnumDropdown(Gtk.ComboBoxText):

    def __init__(self, enum_model: EnumMeta):
        self.reverse_dict: dict[str, Enum] = {}
        store = Gtk.ListStore(str, str)
        for i in enum_model:
            self.reverse_dict.update({EnumLoc[i]: i})
            store.append([EnumLoc[i], EnumLoc[i]])
        super().__init__()
        self.set_model(store)
        self.set_active(0)

    def get_active_member(self) -> Enum:
        str_val = self.get_active_id()
        return self.reverse_dict[str_val]
