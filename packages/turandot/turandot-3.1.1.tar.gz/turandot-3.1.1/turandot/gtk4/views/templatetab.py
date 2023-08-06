import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from turandot.ui import i18n
from turandot.gtk4.representations import TemplateObservable
from turandot.gtk4.presentations import TemplateListView
from turandot.gtk4.views import ViewComponent

# Placeholder to implement localization later
_ = i18n


class TemplateTab(ViewComponent):

    def __init__(self, template_observable: TemplateObservable):
        super().__init__()

        # Template list
        self.template_observable = template_observable
        scrolled_container = Gtk.ScrolledWindow()
        self.template_list = TemplateListView()
        self.template_list.set_vexpand(True)
        self.template_list.set_hexpand(True)
        self.template_observable.attach(self.template_list)
        self.template_observable.notify()
        scrolled_container.set_child(self.template_list)
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
        self.form_title.set_markup("<b>" + _("Add template") + "</b>")
        self.form_title.set_halign(Gtk.Align.START)
        self.form_title.set_margin_bottom(8)

        # Edit form: Select template file
        self.right.attach(self.form_title, 0, 0, 2, 1)
        tf_label = Gtk.Label(label=_("Template file:"))
        self.right.attach(tf_label, 0, 1, 1, 1)
        self.tf_entry = Gtk.Entry()
        self.tf_entry.set_hexpand(True)
        self.right.attach(self.tf_entry, 1, 1, 1, 1)
        self.tf_select_button = Gtk.Button(label=_("Select file"))
        self.tf_select_button.set_halign(Gtk.Align.END)
        self.right.attach(self.tf_select_button, 1, 2, 1, 1)

        # Edit form: Jinja switch
        jinja_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        jinja_container.set_hexpand(True)
        jinja_label = Gtk.Label(label=_("Allow Jinja templating:"))
        jinja_container.append(jinja_label)
        jinja_inner_container = Gtk.Box()
        jinja_inner_container.set_hexpand(True)
        jinja_inner_container.set_halign(Gtk.Align.END)
        self.jinja_switch = Gtk.Switch()
        self.jinja_switch.set_halign(Gtk.Align.END)
        jinja_inner_container.append(self.jinja_switch)
        jinja_container.append(jinja_inner_container)
        self.right.attach(jinja_container, 0, 3, 2, 1)

        # Edit form: Mako switch
        mako_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        mako_container.set_hexpand(True)
        mako_label = Gtk.Label(label=_("Allow Mako templating (DANGEROUS!):"))
        mako_container.append(mako_label)
        mako_inner_container = Gtk.Box()
        mako_inner_container.set_hexpand(True)
        mako_inner_container.set_halign(Gtk.Align.END)
        self.mako_switch = Gtk.Switch()
        self.mako_switch.set_halign(Gtk.Align.END)
        mako_inner_container.append(self.mako_switch)
        mako_container.append(mako_inner_container)
        self.right.attach(mako_container, 0, 4, 2, 1)

        # Edit form: Metadata
        meta_label = Gtk.Label(label=_("Metadata:"))
        meta_label.set_halign(Gtk.Align.START)
        self.right.attach(meta_label, 0, 5, 2, 1)
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
        self.right.attach(meta_scroller, 0, 6, 2, 1)

        # Save button
        self.save_button = Gtk.Button(label=_("Save entry"))
        self.save_button.set_halign(Gtk.Align.END)
        self.right.attach(self.save_button, 1, 7, 1, 1)
