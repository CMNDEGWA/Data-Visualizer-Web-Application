# Data Visualizer

Data Visualizer is a Django application for uploading and analyzing multi-sheet Excel workbooks. 

It discovers worksheets and header rows, automatically maps recognized column names, validates and cleans data, calculates summary metrics, and presents processing results in a dashboard. The current processing pipeline handles **.xlsx** files synchronously and supports a set of fields and metrics.

## Features

- Upload **.xlsx** workbooks up to 15 MB.
- Inspect worksheets and detect likely headers within the first 10 rows.
- Exclude recognized presentation and reference sheets from data processing.
- Automatically map supported column names to standardized fields and assign unmatched headers custom fields.
- Trim text values, skip blank rows, and validate recognized numeric farm-area and harvest values.
- Record upload and processing-job status, processing failures, and validation log entries.
- Calculate sheet and record totals, plus sums for recognized farm-area and harvest fields.
- View metrics, worksheet details, column mappings, and recent processing logs on a dashboard.
- Review recent uploads and delete completed or failed uploads.

### Architecture

        Browser
        │
        ├── Django upload form and views
        │
        ├── Synchronous workbook processing
        │       ├── Inspection: pandas + openpyxl
        │       ├── Column mapping
        │       ├── Validation and cleaning
        │       └── Metric calculation
        │
        ├── PostgreSQL
        │       └── Uploads, jobs, inspections, mappings, metrics, and logs
        │
        └── Django templates + Tailwind CSS
                └── Upload page and results dashboard

### Technology Stack

        Web Application             -           Django
        Database                    -           PostgreSQL
        Excel Processing            -           pandas, openpyxl
        UI Styling                  -           Tailwind CSS (CDN)
        Optional Administration     -           pgAdmin

Celery and Redis are listed in the project dependencies but are not currently connected to the workbook processing workflow. 
        
        Chart.js, Plotly, and Vue.js are not used by the current dashboard.

## Data Processing Workflow

1. **Upload**:
    The upload form accepts **.xlsx** files up to 15 MB. The application stores the workbook and creates upload and processing-job records.

2. **Inspect**:
    The inspector scans workbook sheets, searches the first 10 rows for a likely header row, and records detected headers and row counts. Recognized presentation or reference sheets are excluded from data processing.

3. **Map**:
    The mapper matches supported source headers to standardized fields using built-in aliases. Unmatched headers receive custom field names. Mappings are shown on the dashboard but cannot currently be edited by users.

4. **Validate and Clean**:
    The validator trims text, converts blank values to null, skips and logs blank rows, and converts recognized farm-area and harvest values to numbers. Invalid numeric values generate warnings. Cleaned rows are held in memory during processing and are not persisted as records.

5. **Analyze**:
    The application calculates the number of processed data sheets and records, plus sums for recognized farm-area and harvest fields when numeric values are available.

6. **Persist**:
    The application stores the uploaded file and processing metadata, sheet inspections, column mappings, metric snapshots, and processing logs in PostgreSQL. Processing runs synchronously as part of the upload request; failures update the job and upload status and create an error log.

7. **Present**:
    The dashboard displays file details, discovered sheets and row counts, computed metrics, column mappings and confidence values, and the latest 20 processing logs. It does not currently provide charts or report exports.

### Django Application Structure

        project/
        ├── config/
        │   ├── settings.py
        │   ├── urls.py
        │   ├── asgi.py
        │   └── wsgi.py
        ├── d_analysis/
        │   ├── models.py
        │   ├── views.py
        │   ├── forms.py
        │   ├── urls.py
        │   ├── tests.py
        │   ├── services/
        │   │   ├── workbook_inspector.py
        │   │   ├── column_mapper.py
        │   │   ├── validator.py
        │   │   └── metrics.py
        │   └── templates/d_analysis/
        │       ├── upload.html
        │       └── dashboard.html
        ├── manage.py
        └── requirements.txt

Workbook inspection, mapping, validation, and metric calculations are separated into service modules and called by the Django views.

### Core Data Concepts

- **Upload**:
    Original filename, stored file, file size, upload time, checksum field, and upload status.
- **ProcessingJob**:
    Upload, processing status, start and completion times, processor version, and failure details.
- **SheetInspection**:
    Sheet name, detected header row and headers, row count, validity, and inspection warnings.
- **ColumnMapping**:
    Source header, standardized or custom field, confidence score, and mapping version.
- **MetricSnapshot**:
    Upload, metric name and value, category, and calculation metadata.
- **ProcessingLog**:
    Severity, message, and optional sheet, row, and column details.

Cleaned row data is processed in memory and is not stored in a processed-record or staging table.

#### Dashboard

The dashboard displays:

    - Uploaded file size and number of discovered sheets.
    - Computed metric values, including processed sheet and record totals.
    - Worksheet names, data/reference classification, header counts, and row counts.
    - Automatically generated mappings and their confidence scores.
    - The latest 20 validation and processing log entries.

The dashboard does not currently include charts, editable mappings, data-completeness scores, or export options.
