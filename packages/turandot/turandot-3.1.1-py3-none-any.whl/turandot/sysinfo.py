import sys
import platform
from enum import Enum


class OpSys(Enum):
    LINUX = 0
    WINDOWS = 1
    MACOS = 2


class CpuArch(Enum):
    AMD64 = "amd64"


class SysInfo:
    """Get details about the platform the application is running on"""

    def __init__(self):
        self.system: OpSys = SysInfo._get_system()
        self.arch: CpuArch = SysInfo._get_arch()
        self.frozen: bool = SysInfo._get_frozen()

    @staticmethod
    def _get_system() -> OpSys:
        """Get OS as enum"""
        system = platform.system()
        if system == "Linux":
            return OpSys.LINUX
        if system == "Windows":
            return OpSys.WINDOWS
        if system == "Darwin":
            return OpSys.MACOS
        raise ValueError("Unsupported operating system: {}".format(system))

    @staticmethod
    def _get_arch() -> CpuArch:
        """Get architecture as enum"""
        machine = platform.machine()
        if machine in ['AMD64', 'x86_64']:
            return CpuArch.AMD64
        raise ValueError("Unsupported processor architecture: {}".format(machine))

    @staticmethod
    def _get_frozen() -> bool:
        """Check if application is frozen"""
        return getattr(sys, 'frozen', False)
