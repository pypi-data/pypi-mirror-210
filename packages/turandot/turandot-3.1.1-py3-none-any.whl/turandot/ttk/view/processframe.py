from tkinter import *
from tkinter import ttk

from turandot.ttk.view import TTKStyles
from turandot.ttk.view import ViewComponent


class ProcessFrame(ViewComponent):
    """Create view component to monitor process"""

    def _create_status_labels(self, pframe: ttk.Frame):
        ttk.Label(pframe, text="Status:", style="h2.TLabel", padding=TTKStyles.get_padding().h2_top)\
            .grid(row=0, column=0, sticky=W)
        self.widgets["status_label_value"] = StringVar(value="IDLE")
        ttk.Label(pframe, textvariable=self.widgets["status_label_value"]).grid(row=0, column=1, sticky=E)

    def _create_step_bar(self, pframe: ttk.Frame):
        ttk.Label(pframe, text="Step:").grid(
            row=2, column=0, sticky=W, **TTKStyles.get_padding().left_labels
        )
        n_steps_frame = ttk.Frame(pframe)
        n_steps_frame.grid(
            row=2, column=1, sticky=E, **TTKStyles.get_padding().right_entries
        )
        self.widgets["n_steps_label_value"] = StringVar(value=0)
        ttk.Label(n_steps_frame, textvariable=self.widgets["n_steps_label_value"]).grid(row=0, column=0, sticky=E)
        ttk.Label(n_steps_frame, text="/").grid(row=0, column=1, sticky=E)
        self.widgets["total_steps_label_value"] = StringVar(value=0)
        ttk.Label(n_steps_frame, textvariable=self.widgets["total_steps_label_value"]).grid(row=0, column=2, sticky=E)
        self.widgets["steps_progress_bar"] = ttk.Progressbar(pframe, length=300, mode="determinate", orient=HORIZONTAL)
        self.widgets["steps_progress_bar"].grid(
            row=3, columnspan=2, sticky=(W, E), **TTKStyles.get_padding().full_process_container
        )
        self.widgets["steps_progress_bar"]["value"] = 0
        ttk.Label(pframe, text="Process:").grid(
            row=4, column=0, sticky=W, **TTKStyles.get_padding().left_labels
        )
        self.widgets["current_process_description_label_value"] = StringVar(value="idle")
        ttk.Label(pframe, textvariable=self.widgets["current_process_description_label_value"]).grid(
            row=4, column=1, sticky=E
        )

    def _create_warning_widgets(self, pframe: ttk.Frame):
        self.widgets["warnings_title"] = ttk.Label(pframe, text="Warnings", style="h2.TLabel", padding=TTKStyles.get_padding().h2)
        self.widgets["warnings_title"].grid(row=5, columnspan=2, sticky=(W, E))
        self.widgets["warnings_title"].grid_remove()
        self.widgets["warning_text_view"] = Text(pframe, height=10, width=40)
        self.widgets["warning_text_view"].grid(
            row=6, columnspan=2, sticky=(W, E), **TTKStyles.get_padding().full_process_container
        )
        self.widgets["warning_text_view"].grid_remove()

    def _create_error_widgets(self, pframe: ttk.Frame):
        self.widgets["error_title"] = ttk.Label(pframe, text="Error/Traceback", style="h2.TLabel", padding=TTKStyles.get_padding().h2)
        self.widgets["error_title"].grid(row=7, columnspan=2, sticky=(W, E))
        self.widgets["error_title"].grid_remove()
        self.widgets["error_type_desc_label"] = ttk.Label(pframe, text="Type:")
        self.widgets["error_type_desc_label"].grid(
            row=8, column=0, sticky=W, **TTKStyles.get_padding().left_labels
        )
        self.widgets["error_type_desc_label"].grid_remove()
        self.widgets["error_type_label_value"] = StringVar(value="None")
        self.widgets["error_type_label"] = ttk.Label(pframe, textvariable=self.widgets["error_type_label_value"])
        self.widgets["error_type_label"].grid(row=8, column=1, sticky=E)
        self.widgets["error_type_label"].grid_remove()
        self.widgets["error_text_view"] = Text(pframe, height=10, width=40)
        self.widgets["error_text_view"].grid(
            row=9, columnspan=2, sticky=(W, E), **TTKStyles.get_padding().full_process_container
        )
        self.widgets["error_text_view"].grid_remove()

    def _create_open_button(self, pframe: ttk.Frame):
        self.widgets["open_result_folder"] = ttk.Button(pframe, text="Open folder")
        self.widgets["open_result_folder"].grid(
            row=10, columnspan=2, sticky=E, **TTKStyles.get_padding().right_entries
        )
        self.widgets["open_result_folder"].grid_remove()

    def create(self, add_to: ttk.Frame) -> ttk.Frame:
        pframe = ttk.Frame(add_to)
        pframe.grid(column=0, row=0, sticky=(N, S, W, E))
        pframe.columnconfigure(0, weight=1)
        pframe.columnconfigure(1, weight=1)
        self._create_status_labels(pframe)
        self._create_step_bar(pframe)
        self._create_warning_widgets(pframe)
        self._create_error_widgets(pframe)
        self._create_open_button(pframe)
        return pframe
