from tkinter import *
from tkinter import ttk

from turandot.ttk.presentations import KvCombobox
from turandot.ttk.view.styles import TTKStyles
from turandot.ttk.view import ViewComponent


class ConverterTab(ViewComponent):
    """View component for the 'Convert' tab"""

    def _create_source_widgets(self, cframe: ttk.Frame):
        # Source file title
        test = ttk.Label(cframe, text="Source", style="h2.TLabel", padding=TTKStyles.get_padding().h2_top)
        test.grid(row=0, columnspan=2, sticky=(W, E))
        # Source file select entry
        ttk.Label(cframe, text="Source file:")\
            .grid(row=1, column=0, sticky=W, **TTKStyles.get_padding().left_labels)
        self.widgets["converter_source_file_entry_value"] = StringVar(value="")
        self.widgets["converter_source_file_entry"] = ttk.Entry(
            cframe, textvariable=self.widgets["converter_source_file_entry_value"]
        )
        self.widgets["converter_source_file_entry"].grid(
            row=1, column=1, sticky=(W, E), **TTKStyles.get_padding().right_entries
        )
        # Source file select button
        self.widgets["converter_source_pick_button"] = ttk.Button(cframe, text="Select file")
        self.widgets["converter_source_pick_button"].grid(
            row=2, columnspan=2, sticky=E, **TTKStyles.get_padding().right_entries
        )
        # Template dropdown
        ttk.Label(cframe, text="Template:").grid(row=3, column=0, sticky=W, **TTKStyles.get_padding().left_labels)
        self.widgets["converter_template_dropdown_frame"] = ttk.Frame(cframe)
        self.widgets["converter_template_dropdown_frame"].grid(row=3, column=1, sticky=(W, E))
        self.widgets["converter_template_dropdown_frame"].columnconfigure(0, weight=1)
        # Algorithm dropdown
        ttk.Label(cframe, text="Algorithm:").grid(row=4, column=0, sticky=W, **TTKStyles.get_padding().left_labels)
        self.widgets["converter_algorithm_dropdown_frame"] = ttk.Frame(cframe)
        self.widgets["converter_algorithm_dropdown_frame"].grid(row=4, column=1, sticky=(W, E))
        self.widgets["converter_algorithm_dropdown_frame"].columnconfigure(0, weight=1)

    def _create_reference_widgets(self, cframe: ttk.Frame):
        # Reference title
        ttk.Label(cframe, text="References", style="h2.TLabel", padding=TTKStyles.get_padding().h2)\
            .grid(row=5, columnspan=2, sticky=(W, E))
        # Reference source dropdown
        ttk.Label(cframe, text="Reference data source:").grid(
            row=6, column=0, sticky=W, **TTKStyles.get_padding().left_labels
        )
        self.widgets["converter_reference_source_dropdown_frame"] = ttk.Frame(cframe)
        self.widgets["converter_reference_source_dropdown_frame"].grid(row=6, column=1, sticky=(W, E))
        self.widgets["converter_reference_source_dropdown_frame"].columnconfigure(0, weight=1)
        # CSL dropdown
        self.widgets["converter_csl_label"] = ttk.Label(cframe, text="Citation style:")
        self.widgets["converter_csl_label"].grid(row=7, column=0, sticky=W, **TTKStyles.get_padding().left_labels)
        self.widgets["converter_csl_dropdown_frame"] = ttk.Frame(cframe)
        self.widgets["converter_csl_dropdown_frame"].grid(row=7, column=1, sticky=(W, E))
        self.widgets["converter_csl_dropdown_frame"].columnconfigure(0, weight=1)
        # Zotero widgets
        self.widgets["converter_zotero_lib_label"] = ttk.Label(cframe, text="Zotero library:")
        self.widgets["converter_zotero_lib_label"].grid(
            row=8, column=0, sticky=W, **TTKStyles.get_padding().left_labels
        )
        self.widgets["converter_zotero_lib_dropdown_frame"] = ttk.Frame(cframe)
        self.widgets["converter_zotero_lib_dropdown_frame"].grid(row=8, column=1, sticky=(W, E))
        self.widgets["converter_zotero_lib_dropdown_frame"].columnconfigure(0, weight=1)
        self.widgets["converter_zotero_lib_dropdown"] = KvCombobox(
            self.widgets["converter_zotero_lib_dropdown_frame"], state="readonly"
        )
        self.widgets["converter_zotero_lib_dropdown"].grid(
            row=0, column=0, sticky=(W, E), **TTKStyles.get_padding().right_entries
        )
        self.widgets["converter_zotero_update_button"] = ttk.Button(cframe, text="Update libraries")
        self.widgets["converter_zotero_update_button"].grid(
            row=9, columnspan=2, sticky=E, **TTKStyles.get_padding().right_entries
        )
        # CSLJSON widgets
        self.widgets["converter_csljson_label"] = ttk.Label(cframe, text="CSLJSON file:")
        self.widgets["converter_csljson_label"].grid(row=10, column=0, sticky=W, **TTKStyles.get_padding().left_labels)
        self.widgets["converter_csljson_entry_value"] = StringVar(value="")
        self.widgets["converter_csljson_entry"] = ttk.Entry(
            cframe, textvariable=self.widgets["converter_csljson_entry_value"]
        )
        self.widgets["converter_csljson_entry"].grid(row=10, column=1, sticky=(W, E))
        self.widgets["converter_csljson_pick_button"] = ttk.Button(cframe, text="Select file")
        self.widgets["converter_csljson_pick_button"].grid(
            row=11, columnspan=2, sticky=E, **TTKStyles.get_padding().right_entries
        )

    def _create_export_buttons(self, cframe: ttk.Frame):
        container = ttk.Frame(cframe)
        container.grid(row=12, columnspan=2, sticky=E)
        self.widgets["converter_cancel_export_button"] = ttk.Button(container, text="Cancel export")
        self.widgets["converter_cancel_export_button"].grid(
            row=0, column=0, sticky=E, **TTKStyles.get_padding().inline_buttons
        )
        self.widgets["converter_export_doc_button"] = ttk.Button(container, text="Export document")
        self.widgets["converter_export_doc_button"].grid(
            row=0, column=1, sticky=E, **TTKStyles.get_padding().right_most_inline_button
        )

    def create(self, add_to: ttk.Frame) -> ttk.Frame:
        cframe = ttk.Frame(add_to)
        cframe.grid(column=0, row=0, sticky=(N, S, W, E))
        cframe.columnconfigure(0, weight=0)
        cframe.columnconfigure(1, weight=1)
        self._create_source_widgets(cframe)
        self._create_reference_widgets(cframe)
        self._create_export_buttons(cframe)
        return cframe
