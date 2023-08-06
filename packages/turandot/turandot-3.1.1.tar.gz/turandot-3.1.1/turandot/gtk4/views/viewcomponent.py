from abc import ABC, abstractmethod
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk


class ViewComponent(Gtk.Box):

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.set_margin_top(10)
        self.set_margin_start(10)
        self.set_margin_end(10)
        self.set_margin_bottom(10)
        # self.set_hexpand(True)
        self.left = Gtk.Grid(row_spacing=10, column_spacing=20)
        self.left.set_hexpand(True)
        self.left.set_vexpand(True)
        self.right = Gtk.Grid(row_spacing=10, column_spacing=20)
        self.right.set_hexpand(True)
        self.right.set_vexpand(True)
        self.append(self.left)
        self.append(self.right)
