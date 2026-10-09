# d_analysis/services/validator.py

import pandas as pd
from d_analysis.models import Upload, ProcessingLog

class DataValidator:
    """Cleans data rows, handles missing optional fields, and logs audit warnings."""

    def __init__(self, upload_instance: Upload):
        self.upload = upload_instance
        self.file_path = upload_instance.file.path

    def validate_and_clean_data(self):
        xls = pd.ExcelFile(self.file_path)
        valid_sheets = getattr(self.upload, "sheets", None)
        if valid_sheets is None:
            return {}

        valid_sheets = valid_sheets.filter(is_valid_data_sheet=True)

        cleaned_data_cache = {}

        for sheet in valid_sheets:
            # Re-read sheet, locating header row automatically
            df = pd.read_excel(xls, sheet_name=sheet.sheet_name)
            
            # Clean column names
            df.columns = [str(c).strip() for c in df.columns]
            
            cleaned_rows = []
            for idx, row in df.iterrows():
                row_dict = row.to_dict()
                row_errors = []

                # Basic cleaning: strip strings, convert NaNs to None
                for key, val in row_dict.items():
                    if pd.isna(val):
                        row_dict[key] = None
                    elif isinstance(val, str):
                        row_dict[key] = val.strip()

                if row_errors:
                    ProcessingLog.objects.create(
                        upload=self.upload,
                        severity='WARNING',
                        sheet_name=sheet.sheet_name,
                        row_index=idx + 2, # Excel 1-based row index accounting for header
                        message=f"Validation warnings: {', '.join(row_errors)}"
                    )
                
                cleaned_rows.append(row_dict)
            
            cleaned_data_cache[sheet.sheet_name] = cleaned_rows

        return cleaned_data_cache