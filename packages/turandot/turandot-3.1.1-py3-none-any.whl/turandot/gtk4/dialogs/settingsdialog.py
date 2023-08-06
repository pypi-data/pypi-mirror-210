from itertools import count
from md_citeproc import NotationStyle, OutputStyle
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

from turandot.ui import i18n
from turandot.gtk4.presentations import TitleControl, TextControl, SpinControl, SwitchControl, EnumControl

# Placeholder to implement localization later
_ = i18n


class SettingsDialog(Gtk.Dialog):

    def __init__(self, parent: Gtk.Window):
        super().__init__()
        self.set_transient_for(parent)
        self.set_title(_("Settings"))
        self.set_default_size(width=450, height=600)
        settings_grid = Gtk.Grid(row_spacing=10, column_spacing=10)

        # Create settings widgets
        i = count(start=0, step=1)
        TitleControl(_("General")).attach(settings_grid, next(i))
        SwitchControl(["general", "file_select_persistence"], _("Remember file input path:")).attach(settings_grid, next(i))
        SwitchControl(["general", "save_intermediate"], _("Save intermediate files:")).attach(settings_grid, next(i))
        TitleControl(_("Zotero")).attach(settings_grid, next(i))
        SpinControl(['api', 'zotero', 'port'], _("BetterBibtex Port:")).attach(settings_grid, next(i))
        TitleControl(_("Table of contents")).attach(settings_grid, next(i))
        TextControl(['processors', 'convert_to_html', 'markdown_ext', 'toc', 'marker'], _("TOC marker:")).attach(settings_grid, next(i))
        TitleControl(_("Citeproc")).attach(settings_grid, next(i))
        TextControl(['processors', 'convert_to_html', 'markdown_ext', 'md_citeproc', 'locale'], _("Locale:")).attach(settings_grid, next(i))
        EnumControl(['processors', 'convert_to_html', 'markdown_ext', 'md_citeproc', 'notation'], _("Notation style:"), NotationStyle).attach(settings_grid, next(i))
        EnumControl(['processors', 'convert_to_html', 'markdown_ext', 'md_citeproc', 'output'], _("Output style:"), OutputStyle).attach(settings_grid, next(i))
        TextControl(['processors', 'convert_to_html', 'markdown_ext', 'md_citeproc', 'footnotes_token'], _("Footnote marker:")).attach(settings_grid, next(i))
        TextControl(['processors', 'convert_to_html', 'markdown_ext', 'md_citeproc', 'bibliography_token'], _("Bibliography marker")).attach(settings_grid, next(i))
        TitleControl(_("Optional processors")).attach(settings_grid, next(i))
        SwitchControl(['opt_processors', 'unified_math_block_marker', 'enable'], _("Unified math markers:")).attach(settings_grid, next(i))
        SwitchControl(['opt_processors', 'toc_pagination_containers', 'enable'], _("TOC pagination containers:")).attach(settings_grid, next(i))

        # Attach settings grid
        self.content = self.get_content_area()
        self.content.set_margin_top(10)
        self.content.set_margin_start(10)
        self.content.set_margin_end(10)
        self.content.set_margin_bottom(10)
        scroll_container = Gtk.ScrolledWindow()
        scroll_container.set_child(settings_grid)
        scroll_container.set_vexpand(True)
        scroll_container.set_hexpand(True)
        self.content.append(scroll_container)
