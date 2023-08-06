from tkinter import *
from tkinter import ttk

from turandot.ttk.view.styles import TTKStyles
from turandot.ttk.view import ViewComponent


class CslTab(ViewComponent):
    """View component for the 'csl' tab"""

    def _create_csl_file_selector(self, tframe: ttk.Frame):
        ttk.Label(tframe, text="Entry to edit:").grid(
            row=0, column=0, sticky=W, **TTKStyles.get_padding().left_labels
        )
        self.widgets["csl_editor_dropdown_frame"] = ttk.Frame(tframe)
        self.widgets["csl_editor_dropdown_frame"].grid(row=0, column=1, sticky=(W, E))
        self.widgets["csl_editor_dropdown_frame"].columnconfigure(0, weight=1)
        # self.widgets["csl_editor_dropdown"] = ttk.Combobox(tframe, values=["UNINITIALIZED"])
        # self.widgets["csl_editor_dropdown"].grid(
        #    row=0, column=1, sticky=(W, E), **TTKStyles.get_padding().right_entries
        # )
        ttk.Label(tframe, text="CSL file:").grid(
            row=1, column=0, sticky=W, **TTKStyles.get_padding().left_labels
        )
        self.widgets["csl_base_file_entry_value"] = StringVar(value="")
        self.widgets["csl_base_file_enty"] = ttk.Entry(tframe, textvariable=self.widgets["csl_base_file_entry_value"])
        self.widgets["csl_base_file_enty"].grid(
            row=1, column=1, sticky=(W, E), **TTKStyles.get_padding().right_entries
        )
        self.widgets["csl_select_button"] = ttk.Button(tframe, text="Select file")
        self.widgets["csl_select_button"].grid(
            row=2, columnspan=2, sticky=E, **TTKStyles.get_padding().right_entries
        )

    def _create_csl_buttons(self, tframe: ttk.Frame):
        buttonframe = ttk.Frame(tframe)
        buttonframe.grid(row=4, columnspan=2, sticky=E)
        self.widgets["csl_delete_button"] = ttk.Button(buttonframe, text="Delete entry")
        self.widgets["csl_delete_button"].grid(
            row=0, column=0, sticky=E, **TTKStyles.get_padding().inline_buttons
        )
        self.widgets["csl_delete_button"].state(["disabled"])
        self.widgets["csl_save_button"] = ttk.Button(buttonframe, text="Save entry")
        self.widgets["csl_save_button"].grid(
            row=0, column=1, sticky=E, **TTKStyles.get_padding().right_most_inline_button
        )

    def create(self, add_to: ttk.Frame) -> ttk.Frame:
        cframe = ttk.Frame(add_to)
        cframe.grid(column=0, row=0, sticky=(N, S, W, E))
        cframe.columnconfigure(0, weight=0)
        cframe.columnconfigure(1, weight=1)
        self._create_csl_file_selector(cframe)
        self._create_csl_buttons(cframe)
        return cframe
