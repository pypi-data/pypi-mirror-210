import os

from turandot import SysInfo, OpSys
from turandot.ui import TurandotFrontend
from turandot.model import ModelUtils


class TurandotMain:

    def __init__(self):
        import multiprocessing
        # Solves multiple app start bug when frozen
        multiprocessing.freeze_support()
        # Drastically increases stability of detached Weasyprint conversion process (but lengthens process init time)
        multiprocessing.set_start_method("spawn")
        # Get OS infos
        self.sysinfo = SysInfo()
        # Windows-specific stuff
        if self.sysinfo.system == OpSys.WINDOWS:
            self._prep_windows()
        if self.sysinfo.system == OpSys.LINUX:
            try:
                from turandot.gtk4 import TurandotGtk
                self.frontend: TurandotFrontend = TurandotGtk()
                return
            except ImportError:
                pass
        from turandot.ttk import TurandotTtk
        self.frontend: TurandotFrontend = TurandotTtk()

    @staticmethod
    def _prep_windows():
        """Create fontconfig file on Windows, not really sure if this does any good"""
        target = ModelUtils.get_config_dir() / "fonts.conf"
        if not target.is_file():
            with target.open('w') as fh:
                fh.write(ModelUtils.get_asset_content("windows_fonts.conf"))
        """Set Windows OS specific env variables, maybe obsolete"""
        os.environ['PYTHONUTF8'] = "1"
        os.environ['FONTCONFIG_FILE'] = str(ModelUtils.get_config_dir() / "fonts.conf")

    def main(self):
        self.frontend.run()


def launch():
    """Function to call from pynsist"""
    TurandotMain().main()


if __name__ == "__main__":
    launch()
