import os
import subprocess
from pathlib import Path
from turandot import SysInfo, OpSys


class FrontendUtils:
    """Static utilities for frontends independent of their framework"""

    @staticmethod
    def fm_open_path(*args):
        """Open path in systems file manager"""
        d = None
        for i in args:
            if isinstance(i, Path):
                d = i
                break
        if d is None:
            raise ValueError("No path parameter in func call")
        sysinfo = SysInfo()
        if sysinfo.system == OpSys.WINDOWS:
            os.startfile(d, "explore")
        elif sysinfo.system == OpSys.MACOS:
            subprocess.Popen(['open', d])
        else:
            subprocess.Popen(['xdg-open', d])

    @staticmethod
    def replace_version_number(asset_text: str) -> str:
        """Replace module version number in 'about' tab"""
        from turandot import __version__ as v
        return asset_text.replace("{VER}", v)
