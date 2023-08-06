from typing import Optional
from mako.template import Template as MakoTemplate
from jinja2 import Template as Jinja2Template
from turandot import TurandotConversionException
from turandot.model import ConverterBase, TemplatingEngine, QueueMessage, ConversionJob


class ApplyTemplate(ConverterBase):
    """Apply Jinja or Mako template in current conversion process"""

    DESC: str = "Applying template"
    PREFIX: Optional[str] = "posttmpl_"
    POSTFIX: Optional[str] = ".html"
    SAVABLE: bool = True

    def process_step(self) -> ConversionJob:
        engine = self._get_engine()
        self.conversion_job.current_step.content = self._apply_template(engine)
        return self.conversion_job

    def _get_engine(self) -> TemplatingEngine:
        """Read engine config from config file & database"""
        engine = str(self.conversion_job.job_assets.template.metadata.get("engine", "")).lower()
        if engine.startswith("jinja"):
            if self.conversion_job.job_assets.template.allow_jinja:
                return TemplatingEngine.JINJA2
            else:
                msg = QueueMessage.warningmsg("WARNING: Template metadata suggest Jinja templating, but it is not allowed.")
                self.conversion_job.msgqueue.put(msg)
        elif engine.startswith("mako"):
            if self.conversion_job.job_assets.template.allow_mako:
                return TemplatingEngine.MAKO
            else:
                msg = QueueMessage.warningmsg("WARNING: Template metadata suggest Mako templating, but it is not allowed.")
                self.conversion_job.msgqueue.put(msg)
        return TemplatingEngine.NOTHING

    def _apply_template(self, engine: TemplatingEngine) -> str:
        """Process templating based on type"""
        if engine == TemplatingEngine.JINJA2:
            return self._apply_jinja()
        elif engine == TemplatingEngine.MAKO:
            return self._apply_mako()
        else:
            return self._apply_replace()

    def _apply_jinja(self) -> str:
        """Apply template for Jinja engine"""
        tmpl = Jinja2Template(self.conversion_job.job_assets.template.content)
        try:
            return tmpl.render(
                body=self.conversion_job.current_step.content,
                **self.conversion_job.job_assets.sourcefile.metadata
            )
        except (NameError, RuntimeError):
            raise TurandotConversionException("Jinja conversion error: Probably a missing variable value. Please double-check your YAML header.")

    def _apply_mako(self) -> str:
        """Apply template for Mako engine"""
        tmpl = MakoTemplate(self.conversion_job.job_assets.template.content)
        try:
            return tmpl.render(
                body=self.conversion_job.current_step.content,
                **self.conversion_job.job_assets.sourcefile.metadata
            )
        except (NameError, RuntimeError):
            raise TurandotConversionException("Mako conversion error: Probably a missing variable value. Please double-check your YAML header.")

    def _apply_replace(self) -> str:
        """Apply template for no engine"""
        placeholders = ["${body}", "{{body}}"]
        for i in placeholders:
            if i in self.conversion_job.job_assets.template.content:
                return self.conversion_job.job_assets.template.content.replace(
                    i, self.conversion_job.current_step.content
                )
        raise TurandotConversionException("Conversion error: No placeholder found in template. Try including \"{body}\" in your template file.")
