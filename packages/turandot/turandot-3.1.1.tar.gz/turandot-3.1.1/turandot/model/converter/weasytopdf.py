import uuid
from typing import Optional, Any
from weasyprint import HTML
from pathlib import Path
from turandot import TurandotConversionException, SysInfo, OpSys
from turandot.model import ConverterBase, ConversionJob, QueueMessage


class WeasyprintToPdf(ConverterBase):
    """Use weasyprint to create a PDF file from the HTML step"""

    DESC = "Creating PDF"

    def _write_tmpfile(self) -> Path:
        """Debugging method: Write a temporary file to create a Weasyprint HTML object"""
        enc = self.conversion_job.config.get_key(["general", "encoding"], "utf8")
        tmpfile = self.conversion_job.job_assets.sourcefile.directory / (str(uuid.uuid4()) + ".html")
        with tmpfile.open('w', encoding=enc) as f:
            f.write(self.conversion_job.current_step.content)
        if self.conversion_job.config.get_key(["debug", "weasyprint", "rm_tmp_file"], True):
            self.conversion_job.msgqueue.put(QueueMessage.copymsg((tmpfile, 'f')))
        return tmpfile

    @staticmethod
    def _create_fontconfig() -> Optional["FontConfiguration"]:
        """Create FontConfiguration object to be used by Weasyprint"""
        # sysinfo = SysInfo()
        # if sysinfo.system == OpSys.LINUX:  # FontConfig seems to work fine under Windows
        if True:
            from weasyprint.text.fonts import FontConfiguration
            return FontConfiguration()

    def _create_html_obj(self) -> HTML:
        """Create HTML object for Weasyprint; do it without a temp file if not in debugging mode"""
        filewd = self.conversion_job.job_assets.sourcefile.directory
        enc = self.conversion_job.config.get_key(["general", "encoding"], "utf8")
        if self.conversion_job.config.get_key(["debug", "weasyprint", "use_tmp_file"], False):
            tmpfile = self._write_tmpfile()
            html = HTML(filename=str(tmpfile), encoding=enc)
        else:
            html = HTML(string=self.conversion_job.current_step.content, base_url=str(filewd))
        return html

    def _get_optimizations(self) -> tuple:
        """Read size optimization settings from config file"""
        opt = []
        if self.conversion_job.config.get_key(["processors", "weasyprint_to_pdf", "optimize_size", "images"], True):
            opt.append("images")
        if self.conversion_job.config.get_key(["processors", "weasyprint_to_pdf", "optimize_size", "fonts"], True):
            opt.append("fonts")
        return tuple(opt)

    def _save_pdf(self, html: HTML):
        """Write PDF file"""
        target = self.conversion_job.job_assets.sourcefile.path.with_suffix(".pdf")
        opt = self._get_optimizations()
        fc = WeasyprintToPdf._create_fontconfig()
        try:
            doc = html.render(optimize_size=opt, font_config=fc)
        except IndexError:
            raise TurandotConversionException("Index Error in fontconfig, probably a syntax error in a @font-face rule")
        doc.metadata.generator = "Turandot"
        doc.write_pdf(target=target)

    def process_step(self) -> ConversionJob:
        html = self._create_html_obj()
        self._save_pdf(html)
        return self.conversion_job
