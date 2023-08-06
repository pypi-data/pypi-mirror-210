from pathlib import Path
from tkinter import filedialog

from turandot.model.sql import Repository

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from turandot.ttk.view import TurandotTtkView


class DbFedFilePicker:
    """Util class to draw a file picker dialog"""

    @staticmethod
    def draw(view: "TurandotTtkView", return_id: str, filefilter: list[tuple[str]], title="Choose a file"):
        """Draw file picker dialog"""
        repo = Repository()
        initialdir = repo.get_file_select_persist(return_id)
        chosen = filedialog.askopenfilename(filetypes=filefilter, title=title, initialdir=initialdir)
        if chosen not in [(), ""]:
            repo.set_file_select_persist(return_id, Path(chosen).parent)
            view.widgets[return_id].set(chosen)
