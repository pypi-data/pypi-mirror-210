from tkinter import W, E
from tkinter.messagebox import askyesno
from tkinter import filedialog
from typing import Optional, Type
from enum import Enum

from turandot.model import TemplateAsset, CslAsset
from turandot.ui import background
from turandot.ttk.filetypes import FileTypes
from turandot.ttk.view import TurandotTtkView
from turandot.ttk.view.styles import TTKStyles
from turandot.ttk.controllers import ControllerBase
from turandot.ttk.presentations import \
    DbFedFilePicker, \
    NotificationReason, \
    DatabaseDropdownObservable, \
    TemplateObservable, \
    CslObservable, \
    DatabaseDropdown, \
    DatabaseNewOptDropdown


class DbDropdownController(ControllerBase):
    """Draw comboboxes attached to db fed observables"""

    def __init__(self, view: TurandotTtkView):
        super().__init__(view)

        # Create observables
        self.template_subject = TemplateObservable()
        self.csl_subject = CslObservable()
        # Create Template dropdown on "Converter" Tab
        self.template_selector_dropdown = self._create_dropdown(
            "converter_template_dropdown_frame", "converter_template_dropdown", self.template_subject, DatabaseDropdown
        )
        # Create Template dropdown on "Templates" Tab
        self.template_editor_dropdown = self._create_dropdown(
            "template_editor_dropdown_frame", "template_editor_dropdown", self.template_subject, DatabaseNewOptDropdown
        )
        # Create CSL dropdown on "Converter" Tab
        self.csl_selector_dropdown = self._create_dropdown(
            "converter_csl_dropdown_frame", "converter_csl_dropdown", self.csl_subject, DatabaseDropdown
        )
        # Create CSL dropdown on "CSL" Tab
        self.csl_editor_dropdown = self._create_dropdown(
            "csl_editor_dropdown_frame", "csl_editor_dropdown", self.csl_subject, DatabaseNewOptDropdown
        )
        self._attach_template_tab_events()
        self._attach_csl_tab_events()

    def _create_dropdown(
            self, add_to: str, widget_key: str, observable: DatabaseDropdownObservable, cls: Type[DatabaseDropdown]
    ) -> DatabaseDropdown:
        """Create instance of a combobox with an attached observable"""
        add_to = self.view.widgets.get(add_to)
        self.view.widgets[widget_key] = drpdwn = cls(add_to, state="readonly")
        observable.attach(drpdwn)
        drpdwn.update(observable, reason=NotificationReason.INIT)
        drpdwn.grid(row=0, column=0, sticky=(W, E), **TTKStyles.get_padding().right_entries)
        return drpdwn

    def _attach_template_tab_events(self):
        """Attach callbacks for the template tab"""
        self.template_editor_dropdown.set_callback(self._template_tab_select_callback)
        self.view.widgets["tmpl_delete_button"].bind("<Button-1>", self._template_delete_callback)
        self.view.widgets["tmpl_save_button"].bind("<Button-1>", self._template_save_callback)
        self.view.widgets["tmpl_base_select_button"].bind("<Button-1>", self._template_picker_callback)

    def _attach_csl_tab_events(self):
        """Attach callback for the csl tab"""
        self.csl_editor_dropdown.set_callback(self._csl_tab_select_callback)
        self.view.widgets["csl_save_button"].bind("<Button-1>", self._csl_tab_save_callback)
        self.view.widgets["csl_delete_button"].bind("<Button-1>", self._csl_delete_callback)
        self.view.widgets["csl_select_button"].bind("<Button-1>", self._csl_file_picker)

    def _template_tab_select_callback(self, *args):
        """Attach callback on template selection"""
        dbid = self.template_editor_dropdown.get()
        if dbid == 0:
            self.view.widgets["tmpl_base_file_enty_value"].set("")
            self.view.widgets["tmpl_allow_jinja_value"].set(False)
            self.view.widgets["tmpl_allow_mako_value"].set(False)
            self.view.widgets["tmpl_delete_button"].state(["disabled"])
            return
        tmpl = TemplateAsset.get(dbid=dbid, expand=True)
        self.view.widgets["tmpl_base_file_enty_value"].set(tmpl.path)
        self.view.widgets["tmpl_allow_jinja_value"].set(tmpl.allow_jinja)
        self.view.widgets["tmpl_allow_mako_value"].set(tmpl.allow_mako)
        self.view.widgets["tmpl_delete_button"].state(["!disabled"])

    @background
    def _template_save_callback(self, *args):
        """Attach callback to template save button"""
        dbid = self.template_editor_dropdown.get()
        if dbid == 0:
            tmpl = TemplateAsset(
                path=self.view.widgets["tmpl_base_file_enty_value"].get(),
                allow_jinja=self.view.widgets["tmpl_allow_jinja_value"].get(),
                allow_mako=self.view.widgets["tmpl_allow_mako_value"].get()
            )
            tmpl.save()
            self.template_subject.notify(reason=NotificationReason.NEW)
        else:
            tmpl = TemplateAsset.get(dbid=dbid)
            tmpl.path = self.view.widgets["tmpl_base_file_enty_value"].get()
            tmpl.allow_jinja = self.view.widgets["tmpl_allow_jinja_value"].get()
            tmpl.allow_mako = self.view.widgets["tmpl_allow_mako_value"].get()
            tmpl.save()
            self.template_subject.notify(reason=NotificationReason.CHANGE)

    @background
    def _template_delete_callback(self, *args):
        """Attach callback to template delete button"""
        answer = askyesno("Confirm", "Remove template entry?\n(No files will be deleted)")
        if answer:
            dbid = self.template_editor_dropdown.get()
            tmpl = TemplateAsset.get(dbid=dbid)
            tmpl.delete()
            self.template_subject.notify(reason=NotificationReason.DELETE)

    @background
    def _template_picker_callback(self, *args):
        """Draw file select dialog to pick a template"""
        DbFedFilePicker.draw(self.view, "tmpl_base_file_enty_value", FileTypes.templates)

    def _csl_tab_select_callback(self, *args):
        dbid = self.csl_editor_dropdown.get()
        if dbid == 0:
            self.view.widgets["csl_base_file_entry_value"].set("")
            self.view.widgets["csl_delete_button"].state(["disabled"])
        else:
            csl = CslAsset.get(dbid=dbid)
            self.view.widgets["csl_base_file_entry_value"].set(csl.path)
            self.view.widgets["csl_delete_button"].state(["!disabled"])

    @background
    def _csl_tab_save_callback(self, *args):
        """Attach callback to csl save button"""
        dbid = self.csl_editor_dropdown.get()
        if dbid == 0:
            csl = CslAsset(path=self.view.widgets["csl_base_file_entry_value"].get())
            csl.save()
            self.csl_subject.notify(reason=NotificationReason.NEW)
        else:
            csl = CslAsset.get(dbid=dbid)
            csl.path = self.view.widgets["csl_base_file_entry_value"].get()
            csl.save()
            self.csl_subject.notify(reason=NotificationReason.CHANGE)

    @background
    def _csl_delete_callback(self, *args):
        """Attach callback to csl delete button"""
        answer = askyesno("Confirm", "Remove csl entry?\n(No files will be deleted)")
        if answer:
            dbid = self.csl_editor_dropdown.get()
            csl = CslAsset.get(dbid=dbid)
            csl.delete()
            self.csl_subject.notify(reason=NotificationReason.DELETE)

    @background
    def _csl_file_picker(self, *args):
        """Draw file select dialog to pick a csl file"""
        DbFedFilePicker.draw(self.view, "csl_base_file_entry_value", FileTypes.csl)
