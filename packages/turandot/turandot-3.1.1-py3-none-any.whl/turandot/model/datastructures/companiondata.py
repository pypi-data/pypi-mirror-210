import os
import multiprocessing
from pathlib import Path
from typing import Optional, List, Union
from dataclasses import dataclass, field
from turandot.model import MessageType


@dataclass
class CopyLog:
    """Log created and copied files to delete afterwards"""

    log: List[tuple] = field(default_factory=list)

    def append(self, elem: tuple):
        """
        Append a copied object to the log
        expects type tuple with `d` as second attribute for a directory or `f` for a file
        """
        self.log.append(elem)

    def delete_all(self):
        """Delete all created files and directories on cleanup"""
        self.log.reverse()
        for i in self.log:
            if i[1] == 'f':
                os.remove(i[0])
            elif i[1] == 'd':
                os.rmdir(i[0])


@dataclass
class ConversionStatus:
    """Container class for all status updates coming from the backend"""
    warnings: list = field(default_factory=list)
    exception: Optional[Exception] = None
    exception_hint: str = "No hint available"
    exception_tb: str = ""
    cause_of_death: MessageType = MessageType.CANCELED


class CompanionData:
    """Data class to attach queue to companion thread during conversion"""

    def __init__(self, queue: multiprocessing.Queue):
        self.queue = queue
        self.copylog = CopyLog()
        self.status = ConversionStatus()
