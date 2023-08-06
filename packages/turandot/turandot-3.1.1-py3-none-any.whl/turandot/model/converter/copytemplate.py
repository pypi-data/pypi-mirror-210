import os
import shutil
from pathlib import Path
import zipfile
from turandot import TurandotConversionException
from turandot.model import ConverterBase, ConversionJob, QueueMessage


class CopyTemplate(ConverterBase):
    """Copy all files from the template to conversion directory, log for deletion afterwards"""

    DESC: str = "Copying template data"

    @staticmethod
    def _make_abs_path(relpath: str, destpath: Path) -> Path:
        """Complete relative target path by appending it to conversion directory"""
        for i in relpath.split("/"):
            if i is not None:
                destpath = destpath / i
        return Path(destpath)

    # Recursive Copy & Log
    def _copytree(self, src: Path, dst: Path):
        """Recursively copy a directory tree and log copied files"""
        if not dst.is_dir():
            dst.mkdir()
            self.conversion_job.msgqueue.put(QueueMessage.copymsg((dst, 'd')))
        for item in src.iterdir():
            d = dst / item.name
            if item.is_dir():
                self._copytree(item, d)
            elif item.is_file():
                if d.is_file():
                    raise TurandotConversionException("Template file copy conflict on '{}'".format(d))
                shutil.copy(item, d)
                self.conversion_job.msgqueue.put(QueueMessage.copymsg((d, 'f')))

    def _extract(self, sourcefile: Path, destination: Path):
        """Extract a zip archive and log copied contents"""
        zf = zipfile.ZipFile(sourcefile)
        for i in zf.namelist():
            absp = self._make_abs_path(i, destination)
            if i[-1] == "/":
                if not absp.is_dir():
                    absp.mkdir()
                    self.conversion_job.msgqueue.put(QueueMessage.copymsg((absp, 'd')))
            else:
                if absp.is_file():
                    raise TurandotConversionException("Template file copy conflict on '{}'".format(absp))
                else:
                    with zipfile.ZipFile(sourcefile) as z:
                        z.extract(i, str(destination))
                        self.conversion_job.msgqueue.put(QueueMessage.copymsg((absp, 'f')))

    def process_step(self) -> ConversionJob:
        if self.conversion_job.job_assets.template.zipped:
            self._extract(
                sourcefile=self.conversion_job.job_assets.template.path,
                destination=self.conversion_job.job_assets.sourcefile.directory
            )
        else:
            self._copytree(
                src=self.conversion_job.job_assets.template.directory,
                dst=self.conversion_job.job_assets.sourcefile.directory
            )
        return self.conversion_job
