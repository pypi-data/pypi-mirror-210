import os
from tempfile import NamedTemporaryFile
from tkinter import *
from tkinter import ttk

from turandot.model import ModelUtils
from turandot.ttk.view import TTKStyles
from turandot.ttk.view import ViewComponent
from turandot.ttk.view.convertertab import ConverterTab
from turandot.ttk.view.templatetab import TemplateTab
from turandot.ttk.view.csltab import CslTab
from turandot.ttk.view.settingstab import SettingsTab
from turandot.ttk.view.abouttab import AboutTab
from turandot.ttk.view.processframe import ProcessFrame


class TurandotTtkView:
    """Create view for TK GUI"""

    def __init__(self):
        self.widgets = {}
        self.root = Tk()
        s = ttk.Style()
        self.icon = TurandotTtkView._get_icon()
        pi = PhotoImage(file=self.icon.name)
        self.root.iconphoto(False, pi)
        self.icon.close()
        os.unlink(self.icon.name)
        self.root.title("Turandot")
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        TTKStyles().add_styles(self.root)
        self.mainframe = ttk.Frame(self.root, padding="0 5 0 0")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.mainframe.columnconfigure(0, weight=3)
        self.mainframe.columnconfigure(1, weight=2)
        self.mainframe.rowconfigure(0, weight=1)
        self._assemble_gui()

    @staticmethod
    def _get_icon() -> NamedTemporaryFile:
        """Dump icon to a temp file to use as TK icon"""
        icon = NamedTemporaryFile(mode='wb', delete=False)
        icon.write(ModelUtils.get_asset_bytes("turandot.png"))
        return icon

    def _add_component(self, component: ViewComponent, add_to: Frame) -> ttk.Frame:
        """Add the widgets of a view component to the view"""
        f = component.create(add_to=add_to)
        self.widgets = self.widgets | component.widgets
        return f

    def _create_notebook(self):
        """Create basic notebook widgets to add view components to"""
        notebook = ttk.Notebook(self.mainframe, width=500)
        notebook.grid(column=0, row=0, sticky=(N, W, E, S))
        notebook.columnconfigure(0, weight=1)
        notebook.rowconfigure(0, weight=1)
        # Create Converter Tab
        converter_frame = ttk.Frame(notebook, padding=TTKStyles.get_padding().notebook_frames)
        converter_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        converter_frame.columnconfigure(0, weight=1)
        converter_frame.rowconfigure(0, weight=1)
        # Create Frame in Converter Tab
        self._add_component(ConverterTab(), converter_frame)
        notebook.add(converter_frame, text="Converter")
        # Create Template Tab
        template_frame = ttk.Frame(notebook, padding=TTKStyles.get_padding().no_title_notebook_frames)
        template_frame.grid(column=0, row=0, sticky=(N, E, W, S))
        template_frame.columnconfigure(0, weight=1)
        # Create Frame in Template Tab
        self._add_component(TemplateTab(), template_frame)
        notebook.add(template_frame, text="Templates")
        # Create CSL Tab
        csl_frame = ttk.Frame(notebook, padding=TTKStyles.get_padding().no_title_notebook_frames)
        csl_frame.grid(column=0, row=0, sticky=(N, E, S, W))
        csl_frame.columnconfigure(0, weight=1)
        # Create Frame in CSL Tab
        self._add_component(CslTab(), csl_frame)
        notebook.add(csl_frame, text="CSL")
        # Create Settings Tab
        settings_frame = ttk.Frame(notebook, padding=TTKStyles.get_padding().notebook_frames)
        settings_frame.grid(column=0, row=0, sticky=(N, E, S, W))
        settings_frame.columnconfigure(0, weight=1)
        # Create Frame in Settings Tab
        self._add_component(SettingsTab(), settings_frame)
        notebook.add(settings_frame, text="Settings")
        # Create About Tab
        about_frame = ttk.Frame(notebook, padding=TTKStyles.get_padding().about_notebook_frame)
        about_frame.grid(column=0, row=0, sticky=(N, E, S, W))
        about_frame.columnconfigure(0, weight=1)
        # Create Frame in Settings tab
        self._add_component(AboutTab(), about_frame)
        notebook.add(about_frame, text="About")

    def _create_processframe(self):
        """Add process frame widgets from process frame component"""
        pframe = ttk.Frame(self.mainframe, padding="4 0 12 8")
        pframe.grid(row=0, column=1, sticky=(N, E, S, W))
        pframe.columnconfigure(0, weight=1)
        pframe.rowconfigure(0, weight=1)
        self._add_component(ProcessFrame(), pframe)

    def _assemble_gui(self):
        """Assemble complete view from components"""
        self._create_notebook()
        self._create_processframe()

    def run(self):
        """Run tk main loop after view construction"""
        self.root.mainloop()
