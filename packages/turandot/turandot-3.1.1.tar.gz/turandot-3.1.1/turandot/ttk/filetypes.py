from dataclasses import dataclass


class FileTypesShared:

    all = [("All files", "*")]


class FileTypes(FileTypesShared):
    """Constant class for all file type filters to attach to picker dialogs"""

    markdown = [("Markdown files", ".markdown .mdown .mkdn .mkd .md .txt"), FileTypesShared.all[0]]
    csl = [("CSL files", ".csl .xml"), FileTypesShared.all[0]]
    json = [("JSON files", ".csljson .json"), FileTypesShared.all[0]]
    html = [("HTML files", ".html .html .xml"), FileTypesShared.all[0]]
    templates = [("Template files", ".tmpl .zip .yaml"), FileTypesShared.all[0]]
