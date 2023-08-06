import traceback
import threading
import multiprocessing
from typing import Optional
from turandot.model import ConversionJob, ConverterBase, CompanionData, FrontendStrategy, QueueMessage, MessageType


class ConversionProcessor:
    """
    Processor class to work through conversion chain.
    Conversion is detached in a separate process to make it easily killable.
    Spawn a watchdog thread to wait for subprocess to finish.
    Spawn queue worker thread to read messages from the queue to update frontend
    """

    def __init__(self, conversionjob: ConversionJob, converterchain: ConverterBase, frontendstrat: FrontendStrategy):
        self.conversionjob: ConversionJob = conversionjob
        self.msgqueue: multiprocessing.Queue = self.conversionjob.msgqueue
        self.converterchain: ConverterBase = converterchain
        self.frontendstrat: FrontendStrategy = frontendstrat
        self.conversionproc: Optional[multiprocessing.Process] = None
        self.companiondata: CompanionData = CompanionData(self.msgqueue)

    def _watchdog_worker(self):
        """Check if conversion process still alive, notify queue on death"""
        self.conversionproc.join()
        self.msgqueue.put(QueueMessage.deathmsg())

    def _queue_worker(self):
        """Get messages from queue until conversion dies"""
        while 1:
            msg = self.msgqueue.get(block=True)
            self._process_queue_msg(msg)
            if msg.type == MessageType.DIED:
                break
        self._cleanup()
        self.frontendstrat.handle_companion_data(self.companiondata)

    def _process_queue_msg(self, msg: QueueMessage):
        """Pass queue messages to companion data log and frontend"""
        # Immediately update frontend
        if msg.type in [MessageType.STARTED, MessageType.NEXT_STEP, MessageType.WARNING, MessageType.DIED]:
            if msg.type == MessageType.WARNING:
                self.companiondata.status.warnings.append(msg.warning)
            self.frontendstrat.handle_message(msg)
        # Save data, do something later
        if msg.type == MessageType.COPY:
            self.companiondata.copylog.append(msg.copy)
        if msg.type == MessageType.EXCEPTION:
            self.companiondata.status.exception = msg.exception
            self.companiondata.status.exception_tb = msg.traceback
            self.companiondata.status.cause_of_death = msg.type
        if msg.type == MessageType.SUCCESS:
            self.companiondata.status.cause_of_death = msg.type

    def _cleanup(self):
        """Cleanup all copied files on death"""
        self.companiondata.copylog.delete_all()

    @staticmethod
    def _detached_conversion(conversionjob: ConversionJob, converterchain: ConverterBase):
        """Process complete conversion in different process"""
        try:
            converterchain.handle(conversionjob)
            conversionjob.msgqueue.put(QueueMessage.successmsg())
        except Exception as e:
            tb = traceback.format_exc()
            print(tb)
            conversionjob.msgqueue.put(QueueMessage.exceptionmsg(e, tb))

    def start_conversion(self):
        """Branch off in threads and processes, start conversion"""
        self.msgqueue.put(QueueMessage.startedmsg(self.converterchain.total_steps))
        self.conversionproc = multiprocessing.Process(
            target=self._detached_conversion,
            args=(self.conversionjob, self.converterchain)
        )
        self.conversionproc.start()
        threading.Thread(target=self._queue_worker).start()
        threading.Thread(target=self._watchdog_worker).start()

    def kill_conversion(self):
        """Kill process by force"""
        if self.conversionproc is not None and self.conversionproc.is_alive():
            self.conversionproc.kill()
