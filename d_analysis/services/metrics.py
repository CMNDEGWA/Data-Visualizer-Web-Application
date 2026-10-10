# d_analysis/services/metrics.py

from d_analysis.models import Upload, MetricSnapshot

class MetricsCalculator:
    """This computes summary KPIs and dataset metrics for executive dashboards."""

    def __init__(self, upload_instance: Upload, cleaned_data: dict):
        self.upload = upload_instance
        self.cleaned_data = cleaned_data

    def compute_and_save_metrics(self):
        total_sheets_processed = len(self.cleaned_data)
        total_records = sum(len(rows) for rows in self.cleaned_data.values())

        # Save general aggregate metrics
        MetricSnapshot.objects.create(
            upload=self.upload,
            metric_name='Total Sheets Processed',
            metric_value=float(total_sheets_processed),
            category='Overview'
        )

        MetricSnapshot.objects.create(
            upload=self.upload,
            metric_name='Total Records Analyzed',
            metric_value=float(total_records),
            category='Overview'
        )

        numeric_fields = {
            'farm_area': 'Total Area',
            'harvest_current': 'Current Harvest',
            'harvest_previous': 'Previous Harvest',
        }
        for sheet_name, rows in self.cleaned_data.items():
            for field_name, metric_label in numeric_fields.items():
                values = [
                    row[field_name]
                    for row in rows
                    if isinstance(row.get(field_name), (int, float))
                    and not isinstance(row.get(field_name), bool)
                ]
                if values:
                    MetricSnapshot.objects.create(
                        upload=self.upload,
                        metric_name=f'{metric_label} ({sheet_name})',
                        metric_value=round(sum(values), 4),
                        category='Agronomy',
                        calculation_metadata={'field': field_name, 'value_count': len(values)},
                    )