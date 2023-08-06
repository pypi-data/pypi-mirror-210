import tempfile
import uuid
from copy import copy
from pathlib import Path
from turandot import TurandotAssetException
from turandot.model import ConverterBase, TemplateAsset, CslAsset, TextAsset, SourceAsset, ConversionJob, ReferenceSource, QueueMessage, ZoteroConnector


class GatherData(ConverterBase):
    """Get all data files necessary for the conversion process, complete ConversionJob object"""

    DESC = "Gathering data"

    def _config_interlace(self):
        """
        Override application config with values from document and template
        document takes priority over template
        template takes priority over application
        """
        tmplconfig = self.conversion_job.job_assets.template.metadata.get("turandot_config", {})
        sourceconfig = self.conversion_job.job_assets.sourcefile.metadata.get("turandot_config", {})
        if not isinstance(tmplconfig, dict):
            tmplconfig = {}
        if not isinstance(sourceconfig, dict):
            sourceconfig = {}
        self.conversion_job.config = self.conversion_job.config.interlace(tmplconfig)
        self.conversion_job.config = self.conversion_job.config.interlace(sourceconfig)

    def _force_expand(self):
        """Create expanded asset objects from asset paths"""
        if isinstance(self.conversion_job.job_assets.sourcefile, (str, Path)):
            source = SourceAsset(Path(self.conversion_job.job_assets.sourcefile), expand=True)
            self.conversion_job.job_assets.sourcefile = source
        if isinstance(self.conversion_job.job_assets.template, int):
            tmpl = TemplateAsset.get(dbid=self.conversion_job.job_assets.template, expand=True)
            self.conversion_job.job_assets.template = tmpl
        if isinstance(self.conversion_job.job_assets.cslfile, int):
            csl = CslAsset.get(dbid=self.conversion_job.job_assets.cslfile, expand=True)
            self.conversion_job.job_assets.cslfile = csl
        # Create CSLJSON asset from Zotero lib if necessary
        if self.conversion_job.job_settings.reference_source == ReferenceSource.ZOTERO:
            csljson_drop = self._zotero_to_file(self.conversion_job.job_settings.zotero_lib_id)
            # Log file drop to delete on cleanup
            self.conversion_job.msgqueue.put(QueueMessage.copymsg((csljson_drop, 'f')))
            self.conversion_job.job_assets.csljson = csljson_drop
        if isinstance(self.conversion_job.job_assets.csljson, (str, Path)):
            csljson = TextAsset(Path(self.conversion_job.job_assets.csljson), expand=True)
            self.conversion_job.job_assets.csljson = csljson

    def _zotero_to_file(self, lib_id: int) -> Path:
        """Get CSLJSON data from Zotero & write to a file"""
        filename = "zotero_lib_{}_{}.json".format(lib_id, str(uuid.uuid4()))
        drop_file = Path(tempfile.gettempdir()) / filename
        with drop_file.open('w') as fh:
            fh.write(
                ZoteroConnector(self.conversion_job.config).get_csljson(libid=lib_id)
            )
        return drop_file

    def _check_exceptions(self):
        """Check expansion processes for exceptions: Did anything go wrong while reading files?"""
        for i in self.conversion_job.job_assets:
            if getattr(i, "exception", None) is not None:
                raise i.exception
        if self.conversion_job.job_assets.template is None:
            raise TurandotAssetException("A template for the conversion process must be specified.")
        if self.conversion_job.job_settings.reference_source.value >= ReferenceSource.ZOTERO.value and self.conversion_job.job_assets.cslfile is None:
            raise TurandotAssetException("With the selected reference data source, a citation style must be specified.")

    def process_step(self) -> ConversionJob:
        self._force_expand()
        self._check_exceptions()
        self._config_interlace()
        self.conversion_job.current_step.content = copy(self.conversion_job.job_assets.sourcefile.content)
        return self.conversion_job
