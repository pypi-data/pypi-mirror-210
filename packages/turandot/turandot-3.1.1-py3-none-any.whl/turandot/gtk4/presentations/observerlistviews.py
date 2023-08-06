from typing import Type
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from turandot.model import DatabaseAsset, CslAsset, TemplateAsset
from turandot.gtk4.guithread import guithread
from turandot.gtk4.representations import DatabaseObservable, DataObserver
from turandot.ui import i18n

_ = i18n


# This is technically also a subclass of DataObserver (creates a metaclass conflict)
class ObserverListView(Gtk.TreeView):

    @property
    def MODEL(self) -> Type[DatabaseAsset]:
        raise NotImplementedError

    def __init__(self):
        super().__init__()
        self.store = Gtk.ListStore(str, str)
        self.set_model(self.store)
        self.renderer = Gtk.CellRendererText()
        self.column = Gtk.TreeViewColumn("Templates", self.renderer, text=0)
        self.append_column(self.column)
        self.set_hexpand(True)
        self.set_headers_visible(False)

    @guithread
    def update(self, observable: DatabaseObservable):
        self.store = Gtk.ListStore(str, str)
        self.store.append([_("- new entry -"), "0"])
        for i in observable.entries:
            self.store.append([i.title, str(i.dbid)])
        self.set_model(self.store)
        self.set_cursor(0)

    def get_selected_asset(self) -> DatabaseAsset | None:
        sel = self.get_selection()
        (model, pathlist) = sel.get_selected_rows()
        if len(pathlist) == 0:
            return None
        path = pathlist[0]
        tree_iter = model.get_iter(path)
        dbid = int(model.get_value(tree_iter, 1))
        return self.MODEL.get(dbid, expand=True)


class TemplateListView(ObserverListView):
    MODEL = TemplateAsset


class CslListView(ObserverListView):
    MODEL = CslAsset
