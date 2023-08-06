import multiprocessing
from typing import Optional
from pathlib import Path

from turandot import TurandotAssetException
from turandot.model import ConversionAlgorithm, ReferenceSource, JobSettings, ConversionJob, JobAssets, ConversionProcessor, ConverterChain, SourceAsset
from turandot.ui import catch_exception, FrontendUtils, background
from turandot.ttk.controllers import ControllerBase, TtkConversionUpdater
from turandot.ttk.view import TurandotTtkView


class ExportController(ControllerBase):
    """Controller to handle export and cancel export"""

    def __init__(self, view: TurandotTtkView):
        self.msgqueue = multiprocessing.Queue()
        self.processor: Optional[ConversionProcessor] = None
        ControllerBase.__init__(self, view)
        self.conversion_path: Optional[Path] = None
        self._attach_button_events()

    def _attach_button_events(self):
        """Attach callbacks to export/cancel export buttons"""
        self.view.widgets["converter_export_doc_button"].bind("<Button-1>", self._launch_conversion)
        self.view.widgets["converter_cancel_export_button"].bind("<Button-1>", self._cancel_conversion)

    def _collect_job_settings(self) -> JobSettings:
        """Collect settings for conversion job from GUI"""
        convalg: ConversionAlgorithm = self.view.widgets["converter_algorithm_dropdown"].get()
        refsrc: ReferenceSource = self.view.widgets["converter_reference_source_dropdown"].get()
        if refsrc == ReferenceSource.ZOTERO:
            zotlib: Optional[int] = self.view.widgets["converter_zotero_lib_dropdown"].get()
        else:
            zotlib = None
        return JobSettings(convalg, refsrc, zotlib)

    @catch_exception
    def _collect_job(self) -> Optional[ConversionJob]:
        """Collect settings and assets for conversion job from GUI"""
        settings = self._collect_job_settings()
        srcstring = self.view.widgets["converter_source_file_entry_value"].get()
        if srcstring == "":
            raise TurandotAssetException('Field "Source file" must not be empty')
        srcasset = SourceAsset(path=Path(srcstring), expand=True)
        tmplasset = self.view.widgets["converter_template_dropdown"].get()
        if settings.reference_source.value > 1:
            cslasset = self.view.widgets["converter_csl_dropdown"].get()
        else:
            cslasset = None
        if settings.reference_source == ReferenceSource.JSON:
            csljson = self.view.widgets["converter_csljson_entry_value"].get()
            if csljson == "":
                raise TurandotAssetException('Field "CSLJSON file" must not be empty')
        else:
            csljson = None
        assets = JobAssets(srcasset, tmplasset, cslasset, csljson)
        return ConversionJob(assets, settings, self.msgqueue)

    def _create_processor(self) -> Optional[ConversionProcessor]:
        """Create converter object"""
        job = self._collect_job()
        if job is None:
            return None
        chain = ConverterChain.build_chain(job.job_settings.conversion_algorithm)
        frontendstrat = TtkConversionUpdater(self.view)
        return ConversionProcessor(job, chain, frontendstrat)

    @background
    def _fm_open_conversion_folder(self, *args):
        """Use systems file manager to open conversion directory"""
        if self.conversion_path is not None:
            FrontendUtils.fm_open_path(self.conversion_path)

    def _launch_conversion(self, *args):
        """Launch conversion process"""
        self.processor = self._create_processor()
        if self.processor is None:
            return None
        self.conversion_path = self.processor.conversionjob.job_assets.sourcefile.directory
        self.view.widgets["open_result_folder"].bind("<Button-1>", self._fm_open_conversion_folder)
        self.processor.start_conversion()

    def _cancel_conversion(self, *args):
        """Kill conversion process prematurely"""
        self.processor.kill_conversion()
