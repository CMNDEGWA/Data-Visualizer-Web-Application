# d_analysis/services/workbook_inspector.py

import pandas as pd
from d_analysis.models import Upload, SheetInspection, ProcessingLog

class WorkbookInspector:
    """Dynamically inspects multi-sheet Excel workbooks without hardcoded schemas."""

    def __init__(self, upload_instance: Upload):
        self.upload = upload_instance
        self.file_path = upload_instance.file.path

    def inspect_workbook(self):
        try:
            xls = pd.ExcelFile(self.file_path)
            sheet_names = xls.sheet_names

            inspections = []
            for sheet_name in sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                total_rows = len(df)

                # Heuristic: Find the row that likely contains column headers (non-null density)
                header_row_index = self._detect_header_row(df)
                warnings: list[str] = []

                if header_row_index is not None:
                    headers = df.iloc[header_row_index].dropna().astype(str).tolist()
                    data_row_count = total_rows - (header_row_index + 1)
                    is_valid = True
                else:
                    headers = []
                    data_row_count = 0
                    is_valid = False
                    warnings.append("Could not reliably detect column headers; treated as non-data sheet.")

                # Save inspection metadata to PostgreSQL
                inspection = SheetInspection.objects.create(
                    upload=self.upload,
                    sheet_name=str(sheet_name).strip(),
                    row_count=max(0, data_row_count),
                    detected_headers=headers,
                    is_valid_data_sheet=is_valid,
                    inspection_warnings=warnings
                )
                inspections.append(inspection)

            self.upload.status = 'INSPECTED'
            self.upload.save()
            return inspections

        except Exception as e:
            ProcessingLog.objects.create(
                upload=self.upload,
                severity='ERROR',
                message=f"Workbook inspection failed: {str(e)}"
            )
            self.upload.status = 'FAILED'
            self.upload.save()
            raise e

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