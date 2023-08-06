from turandot.model import FrontendStrategy, CompanionData, QueueMessage, MessageType
from turandot.gtk4.guithread import guithread
from turandot.ui import catch_exception
from turandot.gtk4.enumlocalization import GuiConversionState, EnumLoc
from turandot.gtk4.views import ConverterTab

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from turandot.gtk4 import TurandotMainWindow


class ConversionUpdater(FrontendStrategy):

    def __init__(self, tab: ConverterTab, mainwindow: "TurandotMainWindow"):
        self.tab = tab
        self.mainwindow = mainwindow
        self.warning_string = ""

    def handle_message(self, msg: QueueMessage):
        if msg.type == MessageType.STARTED:
            self._prime_gui(msg)
        elif msg.type == MessageType.NEXT_STEP:
            self._handle_next_step(msg)
        elif msg.type == MessageType.WARNING:
            self._handle_warning(msg)

    @guithread
    @catch_exception
    def handle_companion_data(self, data: CompanionData):
        self.tab.state_label.set_text(EnumLoc[data.status.cause_of_death])
        self.tab.current_process_label.set_text("")
        self.tab.export_button.set_sensitive(True)
        self.tab.cancel_export_button.set_sensitive(False)
        if data.status.cause_of_death == MessageType.SUCCESS:
            self.tab.progress_bar.set_fraction(1.0)
            self.tab.open_folder_button.show()
        else:
            self.tab.progress_bar.set_fraction(0)
        if data.status.exception is not None:
            raise data.status.exception

    @guithread
    def _prime_gui(self, msg: QueueMessage):
        """Reset GUI to default state at the beginning of a conversion"""
        self.tab.state_label.set_text(EnumLoc[GuiConversionState.CONVERTING])
        self.tab.total_steps_label.set_text(str(msg.total_steps))
        self.tab.done_steps_label.set_text("0")
        self.tab.progress_bar.set_fraction(0)
        self.tab.current_process_label.set_text("")
        self.tab.warning_title.hide()
        self.tab.warning_scroll.hide()
        self.warning_string = ""
        self.tab.warning_text_buffer.set_text("")
        self.tab.export_button.set_sensitive(False)
        self.tab.cancel_export_button.set_sensitive(True)
        self.tab.open_folder_button.hide()
        self.mainwindow.error_container.hide()

    @guithread
    def _handle_next_step(self, msg: QueueMessage):
        """Draw information about current conversion step to GUI"""
        self.tab.done_steps_label.set_text(str(msg.n_step))
        self.tab.current_process_label.set_text(msg.step_desc)
        self.tab.progress_bar.set_fraction((msg.n_step - 1) / msg.total_steps)

    @guithread
    def _handle_warning(self, msg: QueueMessage):
        """Draw warning message to GUI"""
        self.warning_string = f"{self.warning_string}{msg.warning}\n"
        self.tab.warning_text_buffer.set_text(self.warning_string)
        self.tab.warning_scroll.show()
        self.tab.warning_title.show()
