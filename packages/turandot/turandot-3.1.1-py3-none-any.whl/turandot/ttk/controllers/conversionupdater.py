from turandot.model import FrontendStrategy, CompanionData, QueueMessage, MessageType
from turandot.ttk.view import TurandotTtkView


class TtkConversionUpdater(FrontendStrategy):
    """Tk specific implementation to update frontend during conversion"""

    STATUS = {
        "idle": "IDLE",
        MessageType.EXCEPTION: "ERROR",
        MessageType.SUCCESS: "SUCCESS",
        MessageType.CANCELED: "CANCELED",
        "conv": "CONVERTING"
    }

    def __init__(self, view: TurandotTtkView):
        self.view = view
        self.warning_string: str = ""

    def _prime_gui(self, msg: QueueMessage):
        """Update GUI at the start of the conversion process"""
        self.view.widgets["open_result_folder"].grid_remove()
        self.view.widgets["status_label_value"].set(self.STATUS["conv"])
        self.view.widgets["n_steps_label_value"].set("0")
        self.view.widgets["total_steps_label_value"].set(str(msg.total_steps))
        self.view.widgets["steps_progress_bar"]["value"] = 0
        self.view.widgets["current_process_description_label_value"].set("")
        self.view.widgets["warnings_title"].grid_remove()
        self.view.widgets["warning_text_view"].grid_remove()
        self.view.widgets["error_title"].grid_remove()
        self.view.widgets["error_type_desc_label"].grid_remove()
        self.view.widgets["error_type_label"].grid_remove()
        self.view.widgets["error_text_view"].grid_remove()
        self.view.widgets["open_result_folder"].grid_remove()
        self.view.widgets["converter_cancel_export_button"].state(["!disabled"])
        self.view.widgets["converter_export_doc_button"].state(["disabled"])

    def _handle_next_step(self, msg: QueueMessage):
        """Update GUI after each step"""
        self.view.widgets["n_steps_label_value"].set(str(msg.n_step))
        self.view.widgets["current_process_description_label_value"].set(msg.step_desc)
        self.view.widgets["steps_progress_bar"]["value"] = ((msg.n_step - 1) / msg.total_steps) * 100

    def _handle_warning(self, msg: QueueMessage):
        """Draw warning onto the GUI"""
        self.warning_string = "{}{}\n".format(self.warning_string, msg.warning)
        self.view.widgets["warning_text_view"].configure(state="normal")
        self.view.widgets["warning_text_view"].delete("1.0", "end")
        self.view.widgets["warning_text_view"].insert('1.0', self.warning_string)
        self.view.widgets["warning_text_view"].configure(state="disabled")
        self.view.widgets["warnings_title"].grid()
        self.view.widgets["warning_text_view"].grid()

    def handle_message(self, msg: QueueMessage):
        if msg.type == MessageType.STARTED:
            self._prime_gui(msg)
        elif msg.type == MessageType.NEXT_STEP:
            self._handle_next_step(msg)
        elif msg.type == MessageType.WARNING:
            self._handle_warning(msg)

    def handle_companion_data(self, data: CompanionData):
        self.view.widgets["status_label_value"].set(self.STATUS[data.status.cause_of_death])
        self.view.widgets["current_process_description_label_value"].set("")
        if data.status.cause_of_death == MessageType.SUCCESS:
            self.view.widgets["steps_progress_bar"]["value"] = 100
            self.view.widgets["open_result_folder"].grid()
        else:
            self.view.widgets["steps_progress_bar"]["value"] = 0
        if data.status.exception is not None:
            self.view.widgets["error_text_view"].configure(state="normal")
            self.view.widgets["error_text_view"].delete("1.0", "end")
            self.view.widgets["error_text_view"].insert(
                '1.0', "{}\n\n{}".format(str(data.status.exception), data.status.exception_tb)
            )
            self.view.widgets["error_text_view"].configure(state="disabled")
            self.view.widgets["error_type_label_value"].set(type(data.status.exception).__name__)
            self.view.widgets["error_title"].grid()
            self.view.widgets["error_type_desc_label"].grid()
            self.view.widgets["error_type_label"].grid()
            self.view.widgets["error_text_view"].grid()
        self.view.widgets["converter_cancel_export_button"].state(["disabled"])
        self.view.widgets["converter_export_doc_button"].state(["!disabled"])
