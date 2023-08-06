import tempfile
import uuid
import shutil
from pathlib import Path
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, Gio

from turandot.model import ModelUtils
from turandot.ui import i18n
from turandot.gtk4.representations import TemplateObservable, CslObservable
from turandot.gtk4.views import ConverterTab, TemplateTab, CslTab, THeaderBar
from turandot.gtk4.controllers import ConverterController, TemplateController, CslController, HeaderBarController

# Placeholder to implement localization later
_ = i18n


class TurandotMainWindow(Gtk.ApplicationWindow):
    """Create the main window to run as GTK4 application"""

    def _load_icon(self):
        """If no icon is available, make a temporary copy and load it"""
        icontheme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        if not icontheme.has_icon("turandot"):
            iconxml = ModelUtils.get_asset_content("turandot.svg")
            self.icon_dir = Path(tempfile.gettempdir()) / ("turandot_icon_" + str(uuid.uuid4()))
            subfolder = self.icon_dir / "hicolor/scalable/actions"
            subfolder.mkdir(parents=True)
            with (subfolder / "turandot.svg").open("w") as f:
                f.write(iconxml)
            icontheme.add_search_path(str(self.icon_dir))
        self.set_icon_name("turandot")

    def _on_destroy(self, *args):
        """Event listener: Clean up after main window is closed"""
        if self.icon_dir is not None:
            shutil.rmtree(self.icon_dir)

    def _load_style(self):
        css = ModelUtils.get_asset_bytes("gtk4.css")
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css)
        screen = Gdk.Display.get_default()
        context = self.get_style_context()
        context.add_provider_for_display(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Instance variables
        self.icon_dir: Path | None = None
        self.root_box: Gtk.Widget | None = None
        self.notebook: Gtk.Widget | None = None
        self.process_box: Gtk.Widget | None = None
        self.error_container: Gtk.Box | None = None
        self.show_error_button: Gtk.Button | None = None
        self.dismiss_error_button: Gtk.Button | None
        # Observables
        self.tmpl_observable = TemplateObservable()
        self.csl_observable = CslObservable()
        # Window basics
        self._create_header()
        self._load_icon()
        self._load_style()
        # Event listeners
        self.connect('close-request', self._on_destroy)
        self.connect('destroy', self._on_destroy)
        # Build views
        self._init_root_box()

    def _create_header(self):
        hb = THeaderBar()
        HeaderBarController(view=hb, mainwindow=self)
        self.set_titlebar(hb)

    def _init_root_box(self):
        """Initialize the top level box element, render views"""
        self.root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self._create_error_container()
        self.notebook = Gtk.Notebook()
        self._fill_notebook()
        self.root_box.append(self.notebook)
        self.set_child(self.root_box)

    def _create_error_container(self):
        self.error_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.error_container.set_margin_start(10)
        self.error_container.set_margin_end(10)
        self.error_container.set_margin_top(10)
        self.error_container.set_margin_bottom(0)
        err_label = Gtk.Label(label=_("An error occurred."))
        err_label.set_hexpand(True)
        err_label.set_halign(Gtk.Align.START)
        self.error_container.append(err_label)
        self.show_error_button = Gtk.Button(label=_("Show traceback"))
        self.error_container.append(self.show_error_button)
        self.dismiss_error_button = Gtk.Button(label=_("Dismiss"))
        self.dismiss_error_button.set_margin_start(10)
        self.error_container.append(self.dismiss_error_button)
        self.error_container.hide()
        self.root_box.append(self.error_container)

    def _fill_notebook(self):
        """Render notebook tabs"""
        conv_tab = ConverterTab(self.tmpl_observable, self.csl_observable)
        ConverterController(view=conv_tab, parent=self)
        tmpl_tab = TemplateTab(self.tmpl_observable)
        TemplateController(view=tmpl_tab, parent=self)
        csl_tab = CslTab(self.csl_observable)
        CslController(view=csl_tab, parent=self)
        self.notebook.append_page(conv_tab, Gtk.Label(label=_("Converter")))
        self.notebook.append_page(tmpl_tab, Gtk.Label(label=_("Templates")))
        self.notebook.append_page(csl_tab, Gtk.Label(label=_("CSL")))
