import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, Gio


class THeaderBar(Gtk.HeaderBar):

    def __init__(self):
        super().__init__()
        self.set_show_title_buttons(True)
        self.set_title_widget(Gtk.Label(label="Turandot"))

        # Create about button
        self.about_button = Gtk.Button()
        about_icon = Gio.ThemedIcon(name="help-about")
        about_image = Gtk.Image.new_from_gicon(about_icon)
        self.about_button.set_child(about_image)
        self.pack_end(self.about_button)

        # Create settings button
        self.settings_button = Gtk.Button()
        settings_icon = Gio.ThemedIcon(name="menu_new")
        settings_image = Gtk.Image.new_from_gicon(settings_icon)
        self.settings_button.set_child(settings_image)
        self.pack_end(self.settings_button)
