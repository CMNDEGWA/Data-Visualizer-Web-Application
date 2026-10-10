# d_analysis/services/column_mapper.py

import re

from d_analysis.models import Upload, ColumnMapping

class ColumnMapper:
    """Maps varying incoming Excel headers to standardized system fields."""

    # Standard header mapping dictionary rules
    STANDARD_DICTIONARY = {
        'farm id': ['unique internal farm id', 'national farm id', 'farm id'],
        'village': ['village', 'city', 'village/ city'],
        'district': ['district', 'state', 'province', 'district/ state/province'],
        'farm_area': ['total farm area', 'farm area (ha)', 'certified crop area'],
        'farm_type': ['farm type', 'small / large'],
        'crop_name': ['certified crop', 'crop'],
        'harvest_current': ['total harvest estimation of current year', 'current harvest'],
        'harvest_previous': ['total harvest of previous year', 'previous harvest'],
    }

    def __init__(self, upload_instance: Upload):
        self.upload = upload_instance

    def auto_map_columns(self):
        """This iterates through sheet inspections and creates ColumnMapping records."""
        sheets = getattr(self.upload, "sheets", None)
        if sheets is None:
            return

        sheets = sheets.filter(is_valid_data_sheet=True)

        for sheet in sheets:
            for header in sheet.detected_headers:
                cleaned_header = header.lower().strip()
                matched_field = self._find_match(cleaned_header)

                confidence = 1.0 if matched_field else 0.0
                if not matched_field:
                    matched_field = f"custom_{cleaned_header.replace(' ', '_')[:30]}"
                    confidence = 0.4

                ColumnMapping.objects.get_or_create(
                    upload=self.upload,
                    sheet_name=sheet.sheet_name,
                    source_header=header,
                    defaults={
                        'standardized_field': matched_field,
                        'confidence_score': confidence
                    }
                )

    def _find_match(self, header_str: str) -> str | None:
        normalized_header = self._normalize_header(header_str)
        matches = []
        for standard_key, aliases in self.STANDARD_DICTIONARY.items():
            for alias in aliases:
                normalized_alias = self._normalize_header(alias)
                if re.search(rf'\b{re.escape(normalized_alias)}\b', normalized_header):
                    matches.append((len(normalized_alias), standard_key))
        return max(matches)[1] if matches else None

    @staticmethod
    def _normalize_header(header: str) -> str:
        return re.sub(r'[^a-z0-9]+', ' ', header.casefold()).strip()