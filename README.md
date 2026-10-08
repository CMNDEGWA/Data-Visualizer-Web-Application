# Data Visualizer

This is a Django application where users can upload, inspect, process and visualizing Excel workbooks with variable sheets and column structures. 

There is a dynamic ingestion and schemas, are not tied to any particular data structure format, it can work with different schemas without needing to be redesigned for each one. The design separates file ingestion from analysis and presentation, so new datasets can be supported.

## Features

- Upload and inspect multi-sheet **.xlsx** workbooks.
- Discover worksheets and headers dynamically.
- Map varying column names to standardized fields.
- Preserve flexible source data for audit and reprocessing.
- Clean and validate rows while tolerating missing optional fields.
- Calculate dataset summaries and configurable KPIs.
- Display results in a responsive dashboard with charts.
- Record processing warnings and errors.
- Export processed summaries and reports.
- Optionally process large workbooks asynchronously.

### Architecture

        Browser
        │
        ├── Django views, forms, authentication
        │
        ├── Upload and workbook inspection
        │       └── pandas + openpyxl
        │
        ├── Validation, mapping, and analysis
        │       ├── PostgreSQL: jobs, mappings, metrics, audit logs
        │       └── JSONB or staging storage: flexible source rows
        │
        ├── Optional background processing
        │       └── Celery + Redis
        │
        └── Django templates + Tailwind CSS
                └── Chart.js or Plotly

### Technology Stack

        Web Application             -           Django
        Database                    -           PostgreSQL
        Database Administration     -           pgAdmin
        Excel Processing            -           pandas, openpyxl
        Background Jobs             -           Celery, Redis
        UI Styling                  -           Tailwind CSS
        Visualization               -           Vue.js, Chart.js or Plotly

## Data Processing Workflow

1. **Upload**:
    A user uploads an Excel workbook. 
    The application validates its file type and size, stores it securely and creates a processing job.

2. **Inspect**:
    The ingestion service discovers workbook sheets, headers and basic column types rather than relying on fixed sheet positions.

3. **Map**:
    Incoming headers are matched to standardized attributes using configured mappings.
    Users can review mappings when automatic matching is incertain.

4. **Validate and Clean**:
    The processor normalizes values, handles blank rows, trim strings, parse dates and converts numeric fields.
    Missing optional fields are recorded as null, malformed values are logged.

5. **Analyze**:
    The application computes available KPIs and distribution summaries based on the recognized fields.

6. **Persist**:
    It stored job metadata, normalised records or flexible source data, aggregate metrics and warnings.

7. **Present or Export**:
    The dashboard displays summaries and charts, with options to download reports and review processing details.

### Django Application Structure

        project/
        ├── config/
        │   ├── settings.py
        │   ├── urls.py
        │   └── celery.py
        ├── analysis/
        │   ├── models.py
        │   ├── views.py
        │   ├── forms.py
        │   ├── urls.py
        │   ├── tasks.py
        │   ├── services/
        │   │   ├── workbook_inspector.py
        │   │   ├── column_mapper.py
        │   │   ├── validator.py
        │   │   └── metrics.py
        │   └── templates/
        ├── manage.py
        └── requirements.txt

Parsing and Analysis logic should be kept in service modules rather than embedding it in views. This makes the pipeline easier to test, reuse and move into Celery tasks.

### Core Data Concepts

- **Upload**:
    original filename, storage path, owner, upload time, checksum and status.
- **ProcessingJobs**:
    upload, status, start/end times, processor version and failure details.
- **SheetInspection**:
    sheet name, detected headers, row count and inspection warnings.
- **ColumnMapping**:
    source header, standardized field, confidence and mappiing version.
- **ProcessedRecord**:
    normalized data, if a stable record model is appropriate.
- **MetricSnapshot**:
    upload or dataset reference, metric name, value and calculation metadata.
- **ProcessingLog**:
    severity, message, sheet, row and column.

#### Dashboard

The dashboard makes processing outcomes clear by including:

    - Summary cards for processed rows, recognized sheets, missing fields and dataset completeness.
    - Charts are only generated when suitable fields are detected.
    - A sheet and column mapping review screen.
    - A warning and errors view with row or column references.
    - Export options for clean data and summary reports.

## Core System Design

### Dynamic Ingestion Pipeline
To accomodate inconsistent Excel structures, the system implements a three-tier mapping layer:

- **Automated Sheet Discovery**:
Dynamically inspects workbook metadata to identify relevsnt tabs regardless of their index position.

- **Flexible Column Mapping**:
Utilizes a staging area with PostgreSQL JSONB fields to store raw rows. This allows the system to capture all incoming data before mapping it to standardized core attributes via user-defined mapping.

- **Graceful Degradation**:
A validation engine that flags missing optional columns as **null** rather than triggering system failures, ensuring the pipeline completes even with incomplete datasets.

### Analysis and Aggregation Engine
Once ingested, the data flows through a transformation pipeline:

- **Cleansing**:
Standardized date formats, trims whitespace and handles missing numeric values.

- **Metric Extraction**:
Computes domain specific KPIs.

- **Relational Persistence**:
Aggregated summaries are moved from the JSONB staging area into optimized relational tables for high performance historical querying and trend analysis.

### Visualization Dashboard
The frontend transforms complex spreadsheet data into an executive summary:

- **KPI Summary Cards**:
High level metrics showing total records processed and data completeness scores.

- **Adaptive Visualizations**:
Charts that auto generate based on the detected data types.

- **Audit Logging**:
A detailed transparency log providing users with warnings regarding malformed data or skipped rows.
