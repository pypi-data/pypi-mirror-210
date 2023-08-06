from copy import deepcopy
import markdown
from importlib import import_module
from turandot.model import ConverterBase, ConversionJob
from markdown_katex.extension import KatexExtension
from md_citeproc import CiteprocExtension
from typing import Optional

from turandot.model import ReferenceSource, QueueMessage


class ConvertToHtml(ConverterBase):
    """Convert preprocessed markdown file to incomplete html body without proper containment"""

    NON_BUILTIN = ['markdown_katex', 'md_citeproc']
    DESC: str = "Converting Markdown to HTML"
    PREFIX = "posthtml_"
    POSTFIX = ".html"
    SAVABLE: bool = True

    def __init__(self):
        self.extensions: list = []
        self.config_builtin: dict = {}
        self.config_non_builtin: dict = {}
        self.citeproc_ext: Optional[CiteprocExtension] = None
        ConverterBase.__init__(self)

    def _load_config(self):
        """Load markdown extension config"""
        ext_config = deepcopy(self.conversion_job.config.get_key(["processors", "convert_to_html", "markdown_ext"], None))
        if ext_config is not None:
            for k, v in ext_config.items():
                if k in ConvertToHtml.NON_BUILTIN:
                    self.config_non_builtin.update({k: v})
                else:
                    self.config_builtin.update({k: v})

    def _create_builtin_extensions(self):
        """Create built-in markdown extensions"""
        for k, v in self.config_builtin.items():
            if v.pop("enable", False):
                mod = import_module("markdown.extensions.{}".format(k), package="markdown")
                ext = mod.makeExtension(**v)
                self.extensions.append(ext)

    def _create_special_extensions(self):
        """Create third party markdown extensions"""
        for k, v in self.config_non_builtin.items():
            # Construct Katex extension
            if k == "markdown_katex" and v.pop("enable", False):
                ext = KatexExtension(**v)
                self.extensions.append(ext)
            # Construct Citeproc extension
            if k == "md_citeproc" and v.pop("enable", False) \
                    and (self.conversion_job.job_settings.reference_source != ReferenceSource.NOTHING):
                self.citeproc_ext = self._create_citeproc_extension(v)
                self.extensions.append(self.citeproc_ext)

    def _create_citeproc_extension(self, citeproc_config) -> CiteprocExtension:
        """
        Explicitly construct CiteprocExtension
        Override csljson, cslfile with values from conversion job
        """
        if self.conversion_job.job_settings.reference_source == ReferenceSource.NOSOURCE:
            citeproc_config["csljson"] = None
            citeproc_config["cslfile"] = None
        else:
            citeproc_config["csljson"] = self.conversion_job.job_assets.csljson.path
            citeproc_config["cslfile"] = self.conversion_job.job_assets.cslfile.path
        return CiteprocExtension(**citeproc_config)

    def process_step(self) -> ConversionJob:
        self._load_config()
        self._create_builtin_extensions()
        self._create_special_extensions()
        self.conversion_job.current_step.content = markdown.markdown(
            self.conversion_job.current_step.content,
            extensions=self.extensions
        )
        if self.citeproc_ext is not None:
            warnings = self.citeproc_ext.get_warnings()
            for i in warnings:
                self.conversion_job.msgqueue.put(QueueMessage.warningmsg(str(i)))
        return self.conversion_job
