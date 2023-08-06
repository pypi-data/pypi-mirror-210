import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from turandot.ui import i18n
from turandot.gtk4.representations import CslObservable
from turandot.gtk4.presentations import CslListView
from turandot.gtk4.views import ViewComponent


_ = i18n


class CslTab(ViewComponent):

    def __init__(self, csl_observable: CslObservable):
        super().__init__()

        # CSL list
        self.csl_observable = csl_observable
        scrolled_container = Gtk.ScrolledWindow()
        self.csl_list = CslListView()
        self.csl_list.set_hexpand(True)
        self.csl_list.set_vexpand(True)
        self.csl_observable.attach(self.csl_list)
        self.csl_observable.notify()
        scrolled_container.set_child(self.csl_list)
        scrolled_container.set_min_content_height(100)
        scrolled_container.set_min_content_width(200)
        self.left.attach(scrolled_container, 0, 0, 1, 1)

        # Add/remove Buttons
        button_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_container.set_hexpand(True)
        button_container.set_halign(Gtk.Align.END)
        self.new_button = Gtk.Button(label=_("New"))
        button_container.append(self.new_button)
        self.delete_button = Gtk.Button(label=_("Remove"))
        self.delete_button.set_margin_start(8)
        self.delete_button.set_sensitive(False)
        button_container.append(self.delete_button)
        self.left.attach(button_container, 0, 1, 1, 1)

        # Edit form: Title
        self.form_title = Gtk.Label()
        self.form_title.set_markup("<b>" + _("Add CSL file") + "</b>")
        self.form_title.set_halign(Gtk.Align.START)
        self.form_title.set_margin_bottom(8)

        # Edit form: Select csl file
        self.right.attach(self.form_title, 0, 0, 2, 1)
        tf_label = Gtk.Label(label=_("CSL file:"))
        self.right.attach(tf_label, 0, 1, 1, 1)
        self.tf_entry = Gtk.Entry()
        self.tf_entry.set_hexpand(True)
        self.right.attach(self.tf_entry, 1, 1, 1, 1)
        self.tf_select_button = Gtk.Button(label=_("Select file"))
        self.tf_select_button.set_halign(Gtk.Align.END)
        self.right.attach(self.tf_select_button, 1, 2, 1, 1)

        # Edit form: Metadata
        meta_label = Gtk.Label(label=_("Metadata:"))
        meta_label.set_halign(Gtk.Align.START)
        self.right.attach(meta_label, 0, 3, 2, 1)
        self.metadata_buf = Gtk.TextBuffer()
        meta_scroller = Gtk.ScrolledWindow()
        meta_scroller.set_hexpand(True)
        meta_scroller.set_min_content_height(120)
        self.metadata_field = Gtk.TextView.new_with_buffer(buffer=self.metadata_buf)
        self.metadata_field.set_editable(False)
        self.metadata_field.set_vexpand(True)
        self.metadata_field.set_hexpand(True)
        self.metadata_field.set_monospace(True)
        meta_scroller.set_child(self.metadata_field)
        self.right.attach(meta_scroller, 0, 4, 2, 1)

        # Save button
        self.save_button = Gtk.Button(label=_("Save entry"))
        self.save_button.set_halign(Gtk.Align.END)
        self.right.attach(self.save_button, 1, 5, 1, 1)