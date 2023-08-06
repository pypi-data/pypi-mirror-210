from tkinter import *
from tkinter import ttk

from turandot.ttk.view.styles import TTKStyles
from turandot.ttk.view import ViewComponent


class TemplateTab(ViewComponent):
    """Create view component for 'Template' tab"""

    def _create_file_template_selector(self, tframe: ttk.Frame):
        ttk.Label(tframe, text="Entry to edit:").grid(
            row=0, column=0, sticky=W, **TTKStyles.get_padding().left_labels
        )
        self.widgets["template_editor_dropdown_frame"] = ttk.Frame(tframe)
        self.widgets["template_editor_dropdown_frame"].grid(row=0, column=1, sticky=(W, E))
        self.widgets["template_editor_dropdown_frame"].columnconfigure(0, weight=1)
        ttk.Label(tframe, text="Template file:").grid(
            row=1, column=0, sticky=W, **TTKStyles.get_padding().left_labels
        )
        self.widgets["tmpl_base_file_enty_value"] = StringVar(value="")
        self.widgets["tmpl_base_file_enty"] = ttk.Entry(tframe, textvariable=self.widgets["tmpl_base_file_enty_value"])
        self.widgets["tmpl_base_file_enty"].grid(
            row=1, column=1, sticky=(W, E), **TTKStyles.get_padding().right_entries
        )
        self.widgets["tmpl_base_select_button"] = ttk.Button(tframe, text="Select file")
        self.widgets["tmpl_base_select_button"].grid(
            row=2, columnspan=2, sticky=E, **TTKStyles.get_padding().right_entries
        )

    def _create_template_switches(self, tframe: ttk.Frame):
        switchframe = ttk.Frame(tframe)
        switchframe.grid(row=3, columnspan=2, sticky=(W, E))
        switchframe.columnconfigure(0, weight=1)
        switchframe.columnconfigure(1, weight=0)
        ttk.Label(switchframe, text="Allow Jinja Templating:").grid(
            row=0, column=0, sticky=W, **TTKStyles.get_padding().left_labels
        )
        self.widgets["tmpl_allow_jinja_value"] = BooleanVar(value=False)
        self.widgets["tmpl_allow_jinja"] = ttk.Checkbutton(
            switchframe, text="", variable=self.widgets["tmpl_allow_jinja_value"]
        )
        self.widgets["tmpl_allow_jinja"].grid(row=0, column=1, sticky=E)
        ttk.Label(switchframe, text="Allow Mako Templating (DANGEROUS!):").grid(
            row=1, column=0, sticky=W, **TTKStyles.get_padding().left_labels
        )
        self.widgets["tmpl_allow_mako_value"] = BooleanVar(value=False)
        self.widgets["tmpl_allow_mako"] = ttk.Checkbutton(
            switchframe, text="", variable=self.widgets["tmpl_allow_mako_value"]
        )
        self.widgets["tmpl_allow_mako"].grid(row=1, column=1, sticky=E)

    def _create_save_del_buttons(self, tframe: ttk.Frame):
        buttonframe = ttk.Frame(tframe)
        buttonframe.grid(row=4, columnspan=2, sticky=E)
        buttonframe.columnconfigure(0, weight=1)
        self.widgets["tmpl_delete_button"] = ttk.Button(buttonframe, text="Delete entry")
        self.widgets["tmpl_delete_button"].state(["disabled"])
        self.widgets["tmpl_delete_button"].grid(
            row=0, column=0, sticky=E, **TTKStyles.get_padding().inline_buttons
        )
        self.widgets["tmpl_save_button"] = ttk.Button(buttonframe, text="Save entry")
        self.widgets["tmpl_save_button"].grid(
            row=0, column=1, sticky=E, **TTKStyles.get_padding().right_most_inline_button
        )

    def create(self, add_to: ttk.Frame) -> ttk.Frame:
        tframe = ttk.Frame(add_to)
        tframe.grid(column=0, row=0, sticky=N+S+E+W)
        tframe.columnconfigure(0, weight=0)
        tframe.columnconfigure(1, weight=1)
        self._create_file_template_selector(tframe)
        self._create_template_switches(tframe)
        self._create_save_del_buttons(tframe)
        return tframe
