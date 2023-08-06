from pathlib import Path
import multiprocessing
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from turandot import TurandotAssetException
from turandot.model import ReferenceSource, ZoteroConnector, ConfigModel, ConversionAlgorithm, ReferenceSource, JobSettings, ConversionJob, JobAssets, ConversionProcessor, ConverterChain, SourceAsset
from turandot.ui import catch_exception, background, i18n, FrontendUtils
from turandot.gtk4.guithread import guithread
from turandot.gtk4.filefilters import FileFilterList
from turandot.gtk4.views import ConverterTab
from turandot.gtk4.controllers import BaseController, ConversionUpdater
from turandot.gtk4.dialogs import FileChooserDialog, FileEntryDbKeys

# Placeholder to implement localization later
_ = i18n


class ConverterController(BaseController):

    def __init__(self, view: ConverterTab, parent: Gtk.Window):
        self.parent = parent
        self.multiqueue = multiprocessing.Queue()
        self.processor: ConversionProcessor | None = None
        self.last_open_folder_id: int | None = None
        super().__init__(view)
        self.connect()

    def connect(self):
        self.view.ref_source_dropdown.connect("changed", self._on_switch_reference_source)
        self.view.zotero_update_button.connect("clicked", self._update_zotero_libs)
        self.view.sf_select_button.connect("clicked", self._on_select_source_file)
        self.view.csljson_button.connect("clicked", self._on_select_json_file)
        self.view.cancel_export_button.connect("clicked", self._cancel_conversion)
        self.view.export_button.connect("clicked", self._launch_conversion)

    def _on_switch_reference_source(self, *args):
        src: ReferenceSource = self.view.ref_source_dropdown.get_active_member()
        if src in [ReferenceSource.NOTHING, ReferenceSource.NOSOURCE]:
            self.view.csl_label.hide()
            self.view.csl_dropdown.hide()
        else:
            self.view.csl_label.show()
            self.view.csl_dropdown.show()
        if src == ReferenceSource.ZOTERO:
            self.view.zotero_label.show()
            self.view.zotero_dropdown.show()
            self.view.zotero_update_button.show()
            self._update_zotero_libs()
        else:
            self.view.zotero_label.hide()
            self.view.zotero_dropdown.hide()
            self.view.zotero_update_button.hide()
        if src == ReferenceSource.JSON:
            self.view.csljson_label.show()
            self.view.csljson_entry.show()
            self.view.csljson_button.show()
        else:
            self.view.csljson_label.hide()
            self.view.csljson_entry.hide()
            self.view.csljson_button.hide()

    @background
    @catch_exception
    def _update_zotero_libs(self, *args):
        libs = ZoteroConnector(ConfigModel().get_dict()).get_libraries()
        store = Gtk.ListStore(str, str)
        for i in libs:
            store.append([i["name"], str(i["id"])])
        self._draw_zotero_libs(store)

    @guithread
    def _draw_zotero_libs(self, store: Gtk.ListStore):
        self.view.zotero_dropdown.set_model(store)
        self.view.zotero_dropdown.set_active(0)

    def _on_select_source_file(self, *args):
        FileChooserDialog.draw_db_fed(
            parent=self.parent,
            return_entry=self.view.sf_entry,
            db_key=FileEntryDbKeys.SourceFileEntry,
            type_filter=FileFilterList.MARKDOWN,
            title=_("Select source file")
        )

    def _on_select_json_file(self, *args):
        FileChooserDialog.draw_db_fed(
            parent=self.parent,
            return_entry=self.view.csljson_entry,
            db_key=FileEntryDbKeys.JsonSourceFile,
            type_filter=FileFilterList.JSON,
            title=_("Select CSLJSON file")
        )

    def _collect_job_settings(self) -> JobSettings:
        """Collect settings for conversion job from GUI"""
        algorithm: ConversionAlgorithm = self.view.algorithm_dropdown.get_active_member()
        reference_source: ReferenceSource = self.view.ref_source_dropdown.get_active_member()
        if reference_source == ReferenceSource.ZOTERO:
            zotero_lib: int | None = int(self.view.zotero_dropdown.get_active_id())
        else:
            zotero_lib = None
        return JobSettings(algorithm, reference_source, zotero_lib)

    @catch_exception
    def _collect_job(self) -> ConversionJob | None:
        settings = self._collect_job_settings()
        srcstring = self.view.sf_entry.get_text()
        if srcstring == "":
            raise TurandotAssetException('Field "Source file must not be empty"')
        srcasset = SourceAsset(path=Path(srcstring), expand=True)
        tmplasset = self.view.template_dropdown.get_selected_asset()
        if settings.reference_source.value > 1:
            cslasset = self.view.csl_dropdown.get_selected_asset()
        else:
            cslasset = None
        if settings.reference_source == ReferenceSource.JSON:
            csljson = self.view.csljson_entry.get_text()
            if csljson == "":
                raise TurandotAssetException('Field "CSLJSON file" must not be empty')
        else:
            csljson = None
        assets = JobAssets(srcasset, tmplasset, cslasset, csljson)
        return ConversionJob(assets, settings, self.multiqueue)

    def _create_processor(self) -> ConversionProcessor | None:
        """Create converter object, containing the prebuilt processor chain, the job and the update strategy"""
        job = self._collect_job()
        if job is None:
            return None
        chain = ConverterChain.build_chain(job.job_settings.conversion_algorithm)
        frontend_strategy = ConversionUpdater(self.view, self.parent)
        return ConversionProcessor(job, chain, frontend_strategy)

    def _reattach_open_folder_callback(self, path: Path):
        """Attach correct path to callback on 'Open Folder' button"""
        if self.last_open_folder_id is not None:
            self.view.open_folder_button.disconnect(self.last_open_folder_id)
        self.last_open_folder_id = self.view.open_folder_button.connect("clicked", FrontendUtils.fm_open_path, path)

    def _launch_conversion(self, *args):
        """Launch conversion process"""
        self.processor = self._create_processor()
        if self.processor is None:
            return None
        self._reattach_open_folder_callback(self.processor.conversionjob.job_assets.sourcefile.directory)
        self.processor.start_conversion()

    def _cancel_conversion(self, *args):
        """Kill conversion process prematurely"""
        if self.processor is not None:
            self.processor.kill_conversion()
