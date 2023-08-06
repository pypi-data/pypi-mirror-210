from md_citeproc import NotationStyle, OutputStyle

from turandot.model import ModelUtils
from turandot.ui import FrontendUtils
from turandot.ttk.controllers import ControllerBase
from turandot.ttk.presentations import TitleControl, TextControl, SpinControl, SwitchControl, TextEnumControl
from turandot.ttk.view import TurandotTtkView


class SettingsController(ControllerBase):
    """Draw settings presentations to settings tab"""

    def __init__(self, view: TurandotTtkView):
        super().__init__(view)
        self._fill_config_file_control()
        self._create_settings_controls()

    def _fill_config_file_control(self):
        """Draw settings file path to GUI"""
        self.view.widgets["config_file_location_entry_value"].set(ModelUtils.get_config_file())
        self.view.widgets["config_dir_open_button"].bind("<Button-1>", SettingsController._open_config_dir)

    @staticmethod
    def _open_config_dir(*args):
        """Open system file manager on config folder"""
        FrontendUtils.fm_open_path(ModelUtils.get_config_dir())
        return "break"

    def _create_settings_controls(self):
        """Draw settings presentations onto GUI"""
        add_to = self.view.widgets.get("settings_container")
        TitleControl("General", add_to, 3)
        SwitchControl("Remember file input path:", ["general", "file_select_persistence"], add_to, 4)
        SwitchControl("Save intermediate files:", ["general", "save_intermediate"], add_to, 5)
        TitleControl("Zotero", add_to, 6)
        SpinControl("BetterBibtex Port:", ['api', 'zotero', 'port'], add_to, 7)
        TitleControl("Table of contents", add_to, 8)
        TextControl("TOC Marker:", ['processors', 'convert_to_html', 'markdown_ext', 'toc', 'marker'], add_to, 9)
        TitleControl("Citeproc", add_to, 10)
        TextControl("Locale:", ['processors', 'convert_to_html', 'markdown_ext', 'md_citeproc', 'locale'], add_to, 11)
        TextEnumControl(
            "Notation Style:",
            ['processors', 'convert_to_html', 'markdown_ext', 'md_citeproc', 'notation'],
            add_to=add_to,
            row=12,
            model=NotationStyle
        )
        TextEnumControl(
            "Output Style:",
            ['processors', 'convert_to_html', 'markdown_ext', 'md_citeproc', 'output'],
            add_to=add_to,
            row=13,
            model=OutputStyle
        )
        TextControl("Footnotes Marker:",
                    ['processors', 'convert_to_html', 'markdown_ext', 'md_citeproc', 'footnotes_token'], add_to, 14)
        TextControl("Bibliography Marker:",
                    ['processors', 'convert_to_html', 'markdown_ext', 'md_citeproc', 'bibliography_token'], add_to, 15)
        TitleControl("Optional processors", add_to, 16)
        SwitchControl("Unified math markers:", ['opt_processors', 'unified_math_block_marker', 'enable'], add_to, 17)
        SwitchControl("TOC pagination containers:",
                      ['opt_processors', 'toc_pagination_containers', 'enable'], add_to, 18)
