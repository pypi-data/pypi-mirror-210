from tkinter import *
from tkinter import ttk

from turandot.ttk.view.styles import TTKStyles
from turandot.ttk.view import ViewComponent


class SettingsTab(ViewComponent):
    """Create view process for 'Settings' tab"""

    def _create_config_file_opener(self, sframe: ttk.Frame):
        ttk.Label(sframe, text="Config file", style="h2.TLabel", padding=TTKStyles.get_padding().h2_top)\
            .grid(row=0, columnspan=2, sticky=(W, E))
        ttk.Label(sframe, text="Location:").grid(
            row=1, column=0, sticky=W, **TTKStyles.get_padding().left_labels
        )
        self.widgets["config_file_location_entry_value"] = StringVar()
        self.widgets["config_file_location_entry"] = ttk.Entry(
            sframe, textvariable=self.widgets["config_file_location_entry_value"], state="readonly"
        )
        self.widgets["config_file_location_entry"].grid(
            row=1, column=1, sticky=(W, E), **TTKStyles.get_padding().right_entries
        )
        self.widgets["config_dir_open_button"] = ttk.Button(sframe, text="Open folder")
        self.widgets["config_dir_open_button"].grid(
            row=2, columnspan=2, sticky=E, **TTKStyles.get_padding().right_entries
        )

    def _create_dynamic_settings_frame(self, sframe: ttk.Frame):
        self.widgets["dynamic_settings_container"] = ttk.Frame(sframe)
        self.widgets["dynamic_settings_container"].grid(row=3, columnspan=2, sticky=(W, E))
        self.widgets["dynamic_settings_container"].columnconfigure(0, weight=0)
        self.widgets["dynamic_settings_container"].columnconfigure(1, weight=1)

    def create(self, add_to: ttk.Frame) -> ttk.Frame:
        self.widgets["settings_container"] = ttk.Frame(add_to)
        self.widgets["settings_container"].grid(column=0, row=0, sticky=(N, S, W, E))
        self.widgets["settings_container"].columnconfigure(0, weight=0)
        self.widgets["settings_container"].columnconfigure(1, weight=1)
        self._create_config_file_opener(self.widgets["settings_container"])
        return self.widgets["settings_container"]
