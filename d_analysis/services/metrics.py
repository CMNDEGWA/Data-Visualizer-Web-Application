# d_analysis/services/metrics.py

from d_analysis.models import Upload, MetricSnapshot

class MetricsCalculator:
    """Computes summary KPIs and dataset metrics for executive dashboards."""

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

        # Domain-specific metric extraction (e.g., Farm Area sums if present)
        for sheet_name, rows in self.cleaned_data.items():
            area_sum = 0.0
            valid_area_count = 0
            
            for row in rows:
                for k, v in row.items():
                    if 'area' in k.lower() and isinstance(v, (int, float)):
                        area_sum += float(v)
                        valid_area_count += 1

            if valid_area_count > 0:
                MetricSnapshot.objects.create(
                    upload=self.upload,
                    metric_name=f'Total Area ({sheet_name})',
                    metric_value=round(area_sum, 4),
                    category='Agronomy'
                )