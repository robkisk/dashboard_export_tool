# Databricks Dashboard Export to PDF & Email

Export large dashboard tables from Databricks AI/BI Dashboards, convert them to PDF, and send via email.

## Features

- Execute SQL queries against Databricks SQL Warehouses
- Export query results to professionally formatted PDF documents
- Email PDF reports with attachments
- Configurable page size, orientation, and styling
- Support for large datasets
- Environment-based configuration
- Support for multiple email providers (Gmail, Outlook, Office365, custom SMTP)

## Prerequisites

- Python 3.8 or higher
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver
- Databricks workspace with SQL Warehouse
- SMTP email account (Gmail, Outlook, Office365, or custom)
- Databricks authentication (token or OAuth)

## Installation

### Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### Setup Project

1. Navigate to the project directory:
```bash
cd dashboard_export_tool
```

2. Sync dependencies with uv:
```bash
uv sync
```

This will:
- Create a virtual environment automatically
- Install all dependencies from `pyproject.toml`
- Generate a `uv.lock` file for reproducible installs

3. Configure Databricks authentication:

The SDK uses standard Databricks authentication. You can configure it in several ways:

**Option A: Environment Variables**
```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-access-token"
```

**Option B: Databricks CLI Configuration**
```bash
databricks configure --token
```

**Option C: .databrickscfg file**
Create `~/.databrickscfg`:
```ini
[DEFAULT]
host = https://your-workspace.cloud.databricks.com
token = your-access-token
```

## Configuration

### 1. Copy the example environment file:
```bash
cp .env.example .env
```

### 2. Edit `.env` with your settings:

```bash
# Databricks Configuration
DATABRICKS_WAREHOUSE_ID=your_warehouse_id

# Optional: Databricks authentication (if not using .databrickscfg)
# DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
# DATABRICKS_TOKEN=your_access_token

# SMTP Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
SMTP_USE_TLS=true

# Export Configuration
EXPORT_OUTPUT_DIR=./exports
EXPORT_PAGE_SIZE=LETTER  # LETTER or A4
EXPORT_ORIENTATION=landscape  # landscape or portrait
EXPORT_MAX_ROWS=10000
```

### Email Provider Settings

**Gmail:**
- SMTP_HOST: `smtp.gmail.com`
- SMTP_PORT: `587`
- Note: Use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password

**Outlook/Hotmail:**
- SMTP_HOST: `smtp-mail.outlook.com`
- SMTP_PORT: `587`

**Office 365:**
- SMTP_HOST: `smtp.office365.com`
- SMTP_PORT: `587`

## Usage

### Basic Usage

Edit `export_dashboard.py` and customize the SQL query and email settings:

```python
# Customize these values in main()
SQL_QUERY = """
SELECT *
FROM your_catalog.your_schema.your_dashboard_table
LIMIT 1000
"""

TO_EMAILS = ['recipient@example.com']
CC_EMAILS = ['cc@example.com']  # Optional
SUBJECT = 'Dashboard Export Report - ' + datetime.now().strftime("%Y-%m-%d")
TITLE = 'AI/BI Dashboard Export'
```

Run the script:
```bash
uv run export_dashboard.py
```

Or activate the virtual environment first:
```bash
# Activate the environment
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Then run normally
python export_dashboard.py
```

### Programmatic Usage

You can also use the `DashboardExporter` class in your own scripts:

```python
from export_dashboard import DashboardExporter
from datetime import datetime

# Initialize exporter
exporter = DashboardExporter(
    warehouse_id="your_warehouse_id",
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_user="your-email@gmail.com",
    smtp_password="your-app-password",
    from_email="your-email@gmail.com"
)

# Execute and export
exporter.export_and_email(
    sql_query="SELECT * FROM catalog.schema.table LIMIT 1000",
    to_emails=["recipient@example.com"],
    subject="Dashboard Report",
    title="My Dashboard Export",
    page_size="LETTER",
    orientation="landscape"
)
```

### Advanced Usage

**Custom PDF Styling:**
```python
# Create PDF only (without email)
data = exporter.execute_query("SELECT * FROM table")
exporter.create_pdf(
    data=data,
    output_path="custom_report.pdf",
    title="Custom Report",
    page_size="A4",
    orientation="portrait"
)
```

**Execute Query Only:**
```python
# Get data for custom processing
data = exporter.execute_query("SELECT * FROM table")
print(f"Retrieved {len(data)} rows")
# Process data as needed...
```

**Send Email Only:**
```python
# Send pre-existing PDF
exporter.send_email(
    to_emails=["recipient@example.com"],
    subject="Report",
    body="Please find attached report",
    pdf_path="./exports/report.pdf",
    cc_emails=["cc@example.com"]
)
```

## Finding Your Warehouse ID

You can find your SQL Warehouse ID in several ways:

**Method 1: Databricks UI**
1. Go to SQL Warehouses in your Databricks workspace
2. Click on your warehouse
3. The ID is in the URL: `/sql/warehouses/{warehouse_id}`

**Method 2: Using the SDK**
```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
warehouses = w.warehouses.list()
for wh in warehouses:
    print(f"Name: {wh.name}, ID: {wh.id}")
```

**Method 3: Databricks CLI**
```bash
databricks sql warehouses list
```

## Scheduling Exports

### Option 1: Databricks Jobs

Create a Databricks Job that runs this script on a schedule:

1. Upload the script to Databricks workspace
2. Create a new Job
3. Set schedule (cron expression)
4. Configure cluster/warehouse
5. Add script as task

### Option 2: Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add entry (e.g., daily at 9 AM)
0 9 * * * cd /path/to/dashboard_export_tool && uv run export_dashboard.py
```

### Option 3: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily, weekly, etc.)
4. Action: Start a program
5. Program: `python`
6. Arguments: `export_dashboard.py`
7. Start in: `C:\path\to\dashboard_export_tool`

## Output

The script generates:
- PDF files in the `exports/` directory (or custom output directory)
- Filename format: `dashboard_export_YYYYMMDD_HHMMSS.pdf`
- Console output showing progress and status

## Troubleshooting

### Authentication Errors

**Problem:** `databricks.sdk.errors.platform.Unauthenticated`

**Solutions:**
- Verify DATABRICKS_HOST and DATABRICKS_TOKEN are set
- Check token hasn't expired
- Ensure you have access to the warehouse

### SMTP Errors

**Problem:** `SMTPAuthenticationError`

**Solutions:**
- For Gmail: Use an App Password, not your regular password
- Enable "Less secure app access" if required
- Check SMTP credentials are correct

### Query Timeout

**Problem:** Query takes too long to execute

**Solutions:**
- Reduce dataset size with LIMIT clause
- Optimize your SQL query
- Use a larger SQL Warehouse
- Increase wait_timeout parameter

### PDF Generation Issues

**Problem:** Table too wide for page

**Solutions:**
- Use landscape orientation
- Reduce number of columns in query
- Use A4 page size for more width

### Large Datasets

**Problem:** Out of memory or timeout with large results

**Solutions:**
- Use LIMIT clause to restrict rows
- Set EXPORT_MAX_ROWS in .env
- For very large exports, consider using Disposition.EXTERNAL_LINKS:

```python
statement = self.w.statement_execution.execute_statement(
    warehouse_id=self.warehouse_id,
    statement=sql_query,
    format=Format.CSV,
    disposition=Disposition.EXTERNAL_LINKS  # Returns download URLs
)
```

## Security Best Practices

1. **Never commit `.env` file** - It contains sensitive credentials
2. **Use App Passwords** - Don't use your main email password
3. **Rotate credentials regularly** - Update tokens and passwords periodically
4. **Limit warehouse access** - Use least-privilege principle
5. **Secure PDF files** - Consider encrypting PDFs with sensitive data

## File Structure

```
dashboard_export_tool/
├── export_dashboard.py   # Main script
├── config.py            # Configuration management
├── example_usage.py     # Example usage scripts
├── pyproject.toml       # Project metadata and dependencies
├── uv.lock             # Lockfile for reproducible installs
├── .env.example        # Example environment file
├── .env               # Your actual config (git-ignored)
├── .gitignore          # Git ignore rules
├── README.md          # This file
├── .venv/             # Virtual environment (created by uv)
└── exports/           # Output directory for PDFs
```

## API Reference

### DashboardExporter

```python
class DashboardExporter:
    def __init__(
        self,
        warehouse_id: str,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str
    )
```

**Methods:**

- `execute_query(sql_query: str) -> List[Dict[str, Any]]`
  - Execute SQL and return results as list of dictionaries

- `create_pdf(data, output_path, title, page_size, orientation) -> str`
  - Generate PDF from data, returns path to created file

- `send_email(to_emails, subject, body, pdf_path, cc_emails)`
  - Send email with PDF attachment

- `export_and_email(sql_query, to_emails, subject, **kwargs)`
  - Complete workflow: query → PDF → email

## Examples

### Example 1: Daily Sales Report

```python
SQL_QUERY = """
SELECT
    date,
    region,
    product,
    sum(revenue) as total_revenue,
    count(distinct customer_id) as customers
FROM sales.daily_summary
WHERE date = current_date() - 1
GROUP BY date, region, product
ORDER BY total_revenue DESC
"""

exporter.export_and_email(
    sql_query=SQL_QUERY,
    to_emails=["sales-team@company.com"],
    subject=f"Daily Sales Report - {datetime.now().strftime('%Y-%m-%d')}",
    title="Daily Sales Performance",
    cc_emails=["manager@company.com"]
)
```

### Example 2: Weekly User Activity

```python
SQL_QUERY = """
SELECT
    user_id,
    username,
    count(*) as sessions,
    sum(duration_minutes) as total_minutes,
    max(last_active) as last_seen
FROM analytics.user_activity
WHERE week = date_trunc('week', current_date() - 7)
GROUP BY user_id, username
ORDER BY sessions DESC
LIMIT 100
"""

exporter.export_and_email(
    sql_query=SQL_QUERY,
    to_emails=["analytics@company.com"],
    subject="Weekly Active Users Report",
    title="Top 100 Active Users - Last Week",
    page_size="A4",
    orientation="landscape"
)
```

## License

This project is provided as-is for use with Databricks SDK.

## Support

For issues related to:
- **Databricks SDK**: https://github.com/databricks/databricks-sdk-py/issues
- **This script**: Check troubleshooting section above

## Development

### Installing Development Dependencies

```bash
# Install with dev dependencies
uv sync --all-extras

# Or just dev dependencies
uv sync --extra dev
```

### Running Tests

```bash
uv run pytest
```

### Code Formatting

```bash
# Format with black
uv run black .

# Lint with ruff
uv run ruff check .
```

### Adding Dependencies

```bash
# Add a new dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Add to a specific optional group
uv add --optional email-providers sendgrid
```

## Contributing

Feel free to customize this script for your needs. Common customizations:
- PDF styling and colors
- Email template formatting
- Query result transformations
- Additional export formats (Excel, CSV, etc.)
- Integration with other services (Slack, Teams, etc.)
