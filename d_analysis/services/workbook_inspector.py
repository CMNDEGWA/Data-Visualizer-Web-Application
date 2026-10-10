# d_analysis/services/workbook_inspector.py

import pandas as pd
from d_analysis.models import Upload, SheetInspection

class WorkbookInspector:
    """This dynamically inspects multi-sheet Excel workbooks without hardcoded schemas."""

    NON_DATA_SHEET_NAMES = {'coverpage', 'guidance', 'dashboard', 'translations'}

    def __init__(self, upload_instance: Upload):
        self.upload = upload_instance
        self.file_path = upload_instance.file.path

    def inspect_workbook(self):
        with pd.ExcelFile(self.file_path) as xls:
            sheet_names = xls.sheet_names

            inspections = []
            for sheet_name in sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                total_rows = len(df)

                header_row_index = self._detect_header_row(df)
                warnings: list[str] = []
                normalized_sheet_name = str(sheet_name).strip().casefold()
                is_known_non_data_sheet = normalized_sheet_name in self.NON_DATA_SHEET_NAMES

                if header_row_index is not None:
                    headers = [
                        str(value).strip()
                        for value in df.iloc[header_row_index].dropna().tolist()
                        if str(value).strip()
                    ]
                    data_row_count = total_rows - (header_row_index + 1)
                else:
                    headers = []
                    data_row_count = 0
                    warnings.append("Could not reliably detect column headers; treated as non-data sheet.")

                is_valid = header_row_index is not None and not is_known_non_data_sheet
                if is_known_non_data_sheet:
                    warnings.append("Recognized as a presentation or reference sheet; not processed as data.")

                inspection = SheetInspection.objects.create(
                    upload=self.upload,
                    sheet_name=str(sheet_name),
                    header_row_index=header_row_index,
                    row_count=max(0, data_row_count),
                    detected_headers=headers,
                    is_valid_data_sheet=is_valid,
                    inspection_warnings=warnings
                )
                inspections.append(inspection)

            return inspections

    def _detect_header_row(self, df: pd.DataFrame, max_rows_to_check: int = 10) -> int | None:
        """Scans top rows to find the most likely header row based on non-empty string counts."""
        best_row: int | None = None
        max_non_null = 0

        check_limit = min(max_rows_to_check, len(df))
        for idx in range(check_limit):
            row_values = df.iloc[idx].dropna()
            non_null_count = len([val for val in row_values if isinstance(val, str) and len(str(val).strip()) > 0])

            if non_null_count > max_non_null:
                max_non_null = non_null_count
                best_row = idx

        return best_row if max_non_null >= 2 else None