import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from md_citeproc import NotationStyle, OutputStyle

from turandot.model import ConversionAlgorithm, ReferenceSource
from turandot.ui import i18n
from turandot.gtk4.representations import CslObservable, TemplateObservable
from turandot.gtk4.presentations import TemplateDropdown, CslDropdown, LocalizedEnumDropdown, TitleControl
from turandot.gtk4.views import ViewComponent


# Placeholder to implement localization later
_ = i18n


class ConverterTab(ViewComponent):
    """View components for the 'Converter' tab"""

    def __init__(self, template_observable: TemplateObservable, csl_observable: CslObservable):
        super().__init__()
        row = 0

        # Create source file selection elements
        source_title = TitleControl(_("Source"))
        source_title.attach(self.left, row)
        row += 1
        sf_label = Gtk.Label(label=_("Source file:"))
        sf_label.set_halign(Gtk.Align.START)
        self.left.attach(sf_label, 0, row, 1, 1)
        self.sf_entry = Gtk.Entry()
        self.sf_entry.set_hexpand(True)
        self.sf_entry.add_css_class("converter-input")
        self.left.attach(self.sf_entry, 1, row, 1, 1)
        row += 1
        self.sf_select_button = Gtk.Button(label=_("Select file"))
        self.sf_select_button.set_halign(Gtk.Align.END)
        self.left.attach(self.sf_select_button, 1, row, 1, 1)
        row += 1

        # Create template selection elements
        tmpl_label = Gtk.Label(label=_("Template:"))
        tmpl_label.set_halign(Gtk.Align.START)
        self.left.attach(tmpl_label, 0, row, 1, 1)
        self.template_dropdown = TemplateDropdown()
        template_observable.attach(self.template_dropdown)
        template_observable.notify()
        self.template_dropdown.set_active(0)
        self.template_dropdown.add_css_class("converter-input")
        self.left.attach(self.template_dropdown, 1, row, 1, 1)
        row += 1

        # Create algorithm selection widgets
        alg_label = Gtk.Label(label=_("Algorithm:"))
        alg_label.set_halign(Gtk.Align.START)
        self.left.attach(alg_label, 0, row, 1, 1)
        self.algorithm_dropdown = LocalizedEnumDropdown(ConversionAlgorithm)
        self.algorithm_dropdown.add_css_class("converter-input")
        self.left.attach(self.algorithm_dropdown, 1, row, 1, 1)
        row += 1

        # Create reference widgets
        ref_title = TitleControl(_("References"))
        ref_title.attach(self.left, row)
        row += 1
        ref_source_label = Gtk.Label(label=_("Reference data source:"))
        ref_source_label.set_halign(Gtk.Align.START)
        self.left.attach(ref_source_label, 0, row, 1, 1)
        self.ref_source_dropdown = LocalizedEnumDropdown(ReferenceSource)
        self.ref_source_dropdown.add_css_class("converter-input")
        self.left.attach(self.ref_source_dropdown, 1, row, 1, 1)
        row += 1
        self.csl_label = Gtk.Label(label=_("Citation style:"))
        self.csl_label.set_halign(Gtk.Align.START)
        self.left.attach(self.csl_label, 0, row, 1, 1)
        self.csl_label.hide()
        self.csl_dropdown = CslDropdown()
        self.csl_dropdown.add_css_class("converter-input")
        csl_observable.attach(self.csl_dropdown)
        csl_observable.notify()
        self.left.attach(self.csl_dropdown, 1, row, 1, 1)
        self.csl_dropdown.hide()
        row += 1
        self.zotero_label = Gtk.Label(label=_("Zotero library:"))
        self.zotero_label.set_halign(Gtk.Align.START)
        self.left.attach(self.zotero_label, 0, row, 1, 1)
        self.zotero_label.hide()
        self.zotero_dropdown = Gtk.ComboBoxText()
        self.zotero_dropdown.add_css_class("converter-input")
        self.left.attach(self.zotero_dropdown, 1, row, 1, 1)
        self.zotero_dropdown.hide()
        row += 1
        self.zotero_update_button = Gtk.Button(label=_("Update library list"))
        self.zotero_update_button.set_halign(Gtk.Align.END)
        self.left.attach(self.zotero_update_button, 1, row, 1, 1)
        self.zotero_update_button.hide()
        row += 1
        self.csljson_label = Gtk.Label(label=_("CSLJSON file:"))
        self.csljson_label.set_halign(Gtk.Align.START)
        self.left.attach(self.csljson_label, 0, row, 1, 1)
        self.csljson_label.hide()
        self.csljson_entry = Gtk.Entry()
        self.csljson_entry.add_css_class("converter-input")
        self.left.attach(self.csljson_entry, 1, row, 1, 1)
        self.csljson_entry.hide()
        row += 1
        self.csljson_button = Gtk.Button(label=_("Select file"))
        self.csljson_button.set_halign(Gtk.Align.END)
        self.left.attach(self.csljson_button, 1, row, 1, 1)
        self.csljson_button.hide()
        row += 1

        # Export/Cancel button container
        button_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_container.set_halign(Gtk.Align.END)
        button_container.set_margin_top(15)
        self.cancel_export_button = Gtk.Button(label=_("Cancel export"))
        self.cancel_export_button.set_sensitive(False)
        button_container.append(self.cancel_export_button)
        self.export_button = Gtk.Button(label=_("Export document"))
        self.export_button.set_margin_start(10)
        button_container.append(self.export_button)
        self.left.attach(button_container, 0, row, 2, 1)

        # Conversion status widgets
        row = 0
        status_title_label = Gtk.Label()
        status_title_label.set_markup("<b>" + _("State:") + "</b>")
        status_title_label.set_halign(Gtk.Align.START)
        self.right.attach(status_title_label, 0, row, 1, 1)
        self.state_label = Gtk.Label(label=_("idle"))
        self.state_label.set_halign(Gtk.Align.END)
        self.state_label.set_hexpand(True)
        self.right.attach(self.state_label, 1, row, 1, 1)
        row += 1
        step_label = Gtk.Label(label=_("Step:"))
        step_label.set_halign(Gtk.Align.START)
        self.right.attach(step_label, 0, row, 1, 1)
        step_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        step_container.set_hexpand(True)
        step_container.set_halign(Gtk.Align.END)
        self.done_steps_label = Gtk.Label(label="0")
        step_container.append(self.done_steps_label)
        slash_label = Gtk.Label(label="/")
        step_container.append(slash_label)
        self.total_steps_label = Gtk.Label(label="0")
        step_container.append(self.total_steps_label)
        self.right.attach(step_container, 1, row, 1, 1)
        row += 1
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.add_css_class("converter-progressbar")
        self.progress_bar.set_hexpand(True)
        self.right.attach(self.progress_bar, 0, row, 2, 1)
        row += 1
        process_label = Gtk.Label(label=_("Process:"))
        process_label.set_halign(Gtk.Align.START)
        self.right.attach(process_label, 0, row, 1, 1)
        self.current_process_label = Gtk.Label(label=_("idle"))
        self.current_process_label.set_halign(Gtk.Align.END)
        self.current_process_label.set_hexpand(True)
        self.right.attach(self.current_process_label, 1, row, 1, 1)
        row += 1

        # Warning widgets
        self.warning_title = TitleControl(_("Warnings"))
        self.warning_title.attach(self.right, row)
        self.warning_title.hide()
        row += 1
        self.warning_scroll = Gtk.ScrolledWindow()
        self.warning_text_buffer = Gtk.TextBuffer()
        self.warning_view = Gtk.TextView()
        self.warning_view.set_buffer(self.warning_text_buffer)
        self.warning_view.set_editable(False)
        self.warning_view.set_monospace(True)
        self.warning_scroll.set_child(self.warning_view)
        self.warning_scroll.set_min_content_height(120)
        self.warning_scroll.set_min_content_width(400)
        self.warning_scroll.hide()
        self.right.attach(self.warning_scroll, 0, row, 2, 1)
        row += 1

        # Open folder button
        self.open_folder_button = Gtk.Button(label=_("Open folder"))
        self.open_folder_button.set_halign(Gtk.Align.END)
        self.open_folder_button.set_margin_top(15)
        self.open_folder_button.hide()
        self.right.attach(self.open_folder_button, 1, row, 1, 1)
