from typing import Optional
from abc import ABC, abstractmethod
from turandot.model import ConversionJob, OptionalStage, QueueMessage


class AbstractConverter(ABC):
    """Base class for optional & mandatory converters, specifies basic interface"""

    def __init__(self):
        self.conversion_job: Optional[ConversionJob] = None

    @abstractmethod
    def handle(self, conversion_job: ConversionJob):
        """Handle a conversion job by processing the current conversion step"""
        pass

    @abstractmethod
    def process_step(self) -> ConversionJob:
        """Execute the current conversion step"""
        pass


class OptionalConverter(AbstractConverter, ABC):
    """Base class for optional converters, can be attached to mandatory converters"""

    @abstractmethod
    def check_config(self, config: dict) -> bool:
        """Check if optional converter is activated"""
        pass

    def handle(self, conversion_job: ConversionJob) -> ConversionJob:
        self.conversion_job = conversion_job
        if self.check_config(conversion_job.config):
            self.process_step()
        return self.conversion_job


class ConverterBase(AbstractConverter, ABC):
    """Base class for mandatory converters, can contain optional converters"""

    DESC: str = ""
    PREFIX: str = ""
    POSTFIX: str = ""
    SAVABLE: bool = False

    def __init__(self):
        AbstractConverter.__init__(self)
        self.optional_converters: tuple[list[OptionalConverter], list[OptionalConverter]] = ([], [])
        self.next_step: Optional[ConverterBase] = None
        self.n_step = 1
        self.total_steps = 1

    def handle(self, conversion_job: ConversionJob):
        self.conversion_job = conversion_job
        self.conversion_job.msgqueue.put(QueueMessage.stepmsg(self.n_step, self.total_steps, self.DESC))
        for i in self.optional_converters[0]:
            self.conversion_job = i.handle(self.conversion_job)
        self.conversion_job = self.process_step()
        for i in self.optional_converters[1]:
            self.conversion_job = i.handle(self.conversion_job)
        self.save_to_file()
        if self.next_step is not None:
            self.next_step.handle(self.conversion_job)

    def save_to_file(self):
        """Save state of current conversion to a file (mainly for debugging)"""
        save_intermediate = False
        general = self.conversion_job.config.get("general", False)
        if general is not False:
            save_intermediate = general.get("save_intermediate", False)
        if self.SAVABLE and save_intermediate:
            self.conversion_job.current_step.filename = self.conversion_job.conversion_id + self.PREFIX + self.POSTFIX
            self.conversion_job.current_step.save_file(self.conversion_job.job_assets.sourcefile.directory)

    def chain_append(self, converter: "ConverterBase"):
        """Append a converter to a chain of converters"""
        self.total_steps += 1
        if self.next_step is None:
            converter.total_steps = self.total_steps
            converter.n_step = self.total_steps
            self.next_step = converter
        else:
            self.next_step.chain_append(converter)

    def register_optional(self, converter: OptionalConverter, stage: OptionalStage = OptionalStage.POST):
        """Register an optional converter to execute before or after this converter"""
        if stage == OptionalStage.PRE:
            self.optional_converters[0].append(converter)
        elif stage == OptionalStage.POST:
            self.optional_converters[1].append(converter)
