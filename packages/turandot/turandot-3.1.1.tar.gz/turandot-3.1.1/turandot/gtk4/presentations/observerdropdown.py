from typing import Type
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from turandot.model import DatabaseAsset, CslAsset, TemplateAsset
from turandot.gtk4.representations import DatabaseObservable, DataObserver


# This is technically also a subclass of DataObserver (creates a metaclass conflict)
class ObserverDropdown(Gtk.ComboBoxText):

    @property
    def MODEL(self) -> Type[DatabaseAsset]:
        raise NotImplementedError

    def update(self, observable: DatabaseObservable):
        store = Gtk.ListStore(str, str)
        for i in observable.entries:
            store.append([i.title, str(i.dbid)])
        self.set_model(store)
        self.set_active(0)

    def get_selected_asset(self) -> DatabaseAsset | None:
        dbid = self.get_active_id()
        if dbid is None:
            return None
        return self.MODEL.get(int(dbid), expand=True)


class TemplateDropdown(ObserverDropdown):
    MODEL = TemplateAsset


class CslDropdown(ObserverDropdown):
    MODEL = CslAsset
