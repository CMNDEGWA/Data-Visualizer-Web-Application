import os
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from d_analysis.models import Upload, ProcessingJob, MetricSnapshot, ProcessingLog
from d_analysis.forms import ExcelUploadForm
from d_analysis.services.workbook_inspector import WorkbookInspector
from d_analysis.services.column_mapper import ColumnMapper
from d_analysis.services.validator import DataValidator
from d_analysis.services.metrics import MetricsCalculator

# Create your views here.
def upload_view(request):
    """Handles workbook upload and triggers the ingestion service pipeline."""
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            
            # Create Upload instance
            upload_instance = Upload.objects.create(
                original_filename=uploaded_file.name,
                file=uploaded_file,
                file_size=uploaded_file.size,
                status='PENDING'
            )
            
            # Create Processing Job tracking record
            job = ProcessingJob.objects.create(
                upload=upload_instance,
                status='RUNNING',
                started_at=timezone.now()
            )

            try:
                # 1. Inspect Workbook Structure (Phase 4 service)
                inspector = WorkbookInspector(upload_instance)
                inspector.inspect_workbook()

                # 2. Auto-map Columns
                mapper = ColumnMapper(upload_instance)
                mapper.auto_map_columns()

                # 3. Validate & Clean Data
                validator = DataValidator(upload_instance)
                cleaned_data = validator.validate_and_clean_data()

                # 4. Calculate & Store Metrics
                calculator = MetricsCalculator(upload_instance, cleaned_data)
                calculator.compute_and_save_metrics()

                job.status = 'SUCCESS'
                job.completed_at = timezone.now()
                job.save()

                return redirect('dashboard_view', upload_id=upload_instance.id)

            except Exception as e:
                job.status = 'ERROR'
                job.error_message = str(e)
                job.completed_at = timezone.now()
                job.save()
                upload_instance.status = 'FAILED'
                upload_instance.save()
                return render(request, 'd_analysis/upload.html', {'form': form, 'error': str(e)})
    else:
        form = ExcelUploadForm()

    recent_uploads = Upload.objects.all().order_by('-uploaded_at')[:5]
    return render(request, 'd_analysis/upload.html', {'form': form, 'recent_uploads': recent_uploads})


def dashboard_view(request, upload_id):
    """Renders the executive summary dashboard with KPIs and logs."""
    upload = get_object_or_404(Upload, id=upload_id)
    sheets = upload.sheets.all()
    metrics = upload.metrics.all()
    logs = upload.logs.all().order_by('-created_at')[:20]
    mappings = upload.mappings.all()

    context = {
        'upload': upload,
        'sheets': sheets,
        'metrics': metrics,
        'logs': logs,
        'mappings': mappings,
    }
    return render(request, 'd_analysis/dashboard.html', context)