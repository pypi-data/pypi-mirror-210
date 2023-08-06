from tkinter import *

from turandot.model import ReferenceSource, ConversionAlgorithm, ZoteroConnector, ConfigModel
from turandot.ui import EnumTranslations, background, catch_exception
from turandot.ttk.controllers import ControllerBase
from turandot.ttk.filetypes import FileTypes
from turandot.ttk.presentations import EnumCombobox, DbFedFilePicker
from turandot.ttk.view import TTKStyles
from turandot.ttk.view import TurandotTtkView


class ConverterController(ControllerBase):
    """Controller to add and handle comboboxes on controller tab"""

    def __init__(self, view: TurandotTtkView):
        super().__init__(view)
        self._attach_button_events()
        self._add_enum_dropdowns()

    def _attach_button_events(self):
        """Handle button press events"""
        self.view.widgets["converter_zotero_update_button"].bind("<Button-1>", self._update_zotero_libs)
        self.view.widgets["converter_cancel_export_button"].state(["disabled"])
        self.view.widgets["converter_source_pick_button"].bind("<Button-1>", self._source_picker_callback)
        self.view.widgets["converter_csljson_pick_button"].bind("<Button-1>", self._csljson_picker_callback)

    @background
    def _source_picker_callback(self, *args):
        """Draw file picker dialog on select source button"""
        DbFedFilePicker.draw(self.view, "converter_source_file_entry_value", FileTypes.markdown)
        return "break"

    @background
    def _csljson_picker_callback(self, *args):
        """Draw file picker dialog on select csljson button"""
        DbFedFilePicker.draw(self.view, "converter_csljson_entry_value", FileTypes.json)
        return "break"

    def _add_enum_dropdowns(self):
        """Add various comboboxes from enums"""
        m = self.view.widgets["converter_reference_source_dropdown_frame"]
        self.view.widgets["converter_reference_source_dropdown"] = EnumCombobox(
            m, ReferenceSource, EnumTranslations.textentries, state="readonly"
        )
        self.view.widgets["converter_reference_source_dropdown"].grid(
            row=0, column=0, sticky=(W, E), **TTKStyles.get_padding().right_entries
        )
        self.view.widgets["converter_reference_source_dropdown"].set_callback(self._ref_source_callback)
        self.view.widgets["converter_reference_source_dropdown"].current(0)
        m = self.view.widgets["converter_algorithm_dropdown_frame"]
        self.view.widgets["converter_algorithm_dropdown"] = EnumCombobox(
            m, ConversionAlgorithm, EnumTranslations.textentries, state="readonly"
        )
        self.view.widgets["converter_algorithm_dropdown"].grid(
            row=0, column=0, sticky=(W, E), **TTKStyles.get_padding().right_entries
        )
        self.view.widgets["converter_algorithm_dropdown"].current(0)

    def _ref_source_callback(self, *args):
        """Draw various widgets specific to the selected reference source"""
        refsource = self.view.widgets["converter_reference_source_dropdown"].get()
        if refsource.value <= 1:
            self.view.widgets["converter_csl_label"].grid_remove()
            self.view.widgets["converter_csl_dropdown_frame"].grid_remove()
        else:
            self.view.widgets["converter_csl_label"].grid()
            self.view.widgets["converter_csl_dropdown_frame"].grid()
        if refsource == ReferenceSource.ZOTERO:
            self.view.widgets["converter_zotero_lib_dropdown_frame"].grid()
            self.view.widgets["converter_zotero_lib_label"].grid()
            self.view.widgets["converter_zotero_update_button"].grid()
            self._update_zotero_libs()
        else:
            self.view.widgets["converter_zotero_lib_dropdown_frame"].grid_remove()
            self.view.widgets["converter_zotero_lib_label"].grid_remove()
            self.view.widgets["converter_zotero_update_button"].grid_remove()
        if refsource == ReferenceSource.JSON:
            self.view.widgets["converter_csljson_label"].grid()
            self.view.widgets["converter_csljson_entry"].grid()
            self.view.widgets["converter_csljson_pick_button"].grid()
        else:
            self.view.widgets["converter_csljson_label"].grid_remove()
            self.view.widgets["converter_csljson_entry"].grid_remove()
            self.view.widgets["converter_csljson_pick_button"].grid_remove()

    @background
    @catch_exception
    def _update_zotero_libs(self, *args):
        """Update comboboxes based on available zotero libraries"""
        self.view.widgets["converter_zotero_lib_dropdown"].clear()
        libs = ZoteroConnector(ConfigModel().get_dict()).get_libraries()
        for i in libs:
            self.view.widgets["converter_zotero_lib_dropdown"].add_option(i["id"], i["name"])
        self.view.widgets["converter_zotero_lib_dropdown"].current(0)
        return "break"
