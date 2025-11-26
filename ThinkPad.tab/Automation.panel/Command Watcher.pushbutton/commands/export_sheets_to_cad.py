# -*- coding: utf-8 -*-
import os, json, clr
from pyrevit import forms
from Autodesk.Revit.DB import (
    FilteredElementCollector,
    BuiltInCategory,
    ViewSheet,
    DWGExportOptions,
    DXFExportOptions,
    ElementId
)

# Import List for proper ICollection conversion
clr.AddReference("System")
from System.Collections.Generic import List


def run(uiapp, data, log):
    """Exports selected Revit sheets to DWG or DXF."""
    try:
        doc = uiapp.ActiveUIDocument.Document

        # Extract parameters
        sheet_ids = data.get("sheet_ids", [])
        cad_format = data.get("cad_format", "dwg").lower()
        export_path = data.get("path", r"C:\PADApps\RevitPAD\Exports")

        if not os.path.exists(export_path):
            os.makedirs(export_path)

        log("Starting export_sheets_to_cad -> {0}".format(export_path))
        log("Format: {0} | Sheets: {1}".format(cad_format, len(sheet_ids)))

        # Choose export options
        if cad_format == "dxf":
            options = DXFExportOptions()
        else:
            options = DWGExportOptions()


        # Prevent Xrefs and separate files
        try: 
            options.ExportViewsAsExternalReferences = False
        except: 
            pass

        # Merge all sheet views into a single DWG
        try:
            options.MergedViews = True
        except:
            pass

        # Prevent coordinates/export splitting
        try:
            options.SharedCoords = False
        except:
            pass

        # Prevent Revit from exporting parts of sheets separately
        try:
            options.ExportingAreas = False
        except:
            pass

        # Collect target sheets
        all_sheets = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Sheets)
        # If sheet_ids is empty, export everything
        if not sheet_ids:
            export_sheets = all_sheets
        else:
            export_sheets = [s for s in all_sheets if s.Id.IntegerValue in sheet_ids]

        if not export_sheets:
            msg = "⚠️ No matching sheets found for export."
            log(msg)
            forms.alert(msg, title="Revit Command Watcher")
            return

        # Export loop
        exported = []
        for sheet in export_sheets:
            try:
                sheetnum = sheet.SheetNumber
                sheetname = sheet.Name

                # Build safe filename (no f-strings allowed)
                combined = "{0}_{1}".format(sheetnum, sheetname)
                safe_name = "".join([c for c in combined if c.isalnum() or c in ("_", "-")])

                views = List[ElementId]([sheet.Id])  # ICollection[ElementId]
                result = doc.Export(export_path, safe_name, views, options)

                if result:
                    file_path = os.path.join(export_path, safe_name + "." + cad_format)
                    exported.append(file_path)
                    log("Exported: {0}".format(file_path))

            except Exception as e:
                log("Failed to export sheet {0}: {1}".format(sheet.SheetNumber, e))

        msg = "Export complete: {0} files exported to\n{1}".format(len(exported), export_path)
        log(msg)
        forms.alert(msg, title="Revit Command Watcher")

    except Exception as e:
        log("Error in export_sheets_to_cad: {0}".format(e))
