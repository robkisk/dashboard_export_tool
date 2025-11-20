#!/usr/bin/env python3
"""
Databricks AI/BI Dashboard Export to PDF and Email

This script exports a large dashboard table from Databricks AI/BI Dashboards,
converts it to PDF, and sends it via email.
"""

import os
import sys
import csv
import io
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState, Format, Disposition
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class DashboardExporter:
    """Export Databricks dashboard query results to PDF and email."""

    def __init__(
        self,
        warehouse_id: str,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
        from_email: str
    ):
        """
        Initialize the dashboard exporter.

        Args:
            warehouse_id: Databricks SQL warehouse ID
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            smtp_user: SMTP authentication username
            smtp_password: SMTP authentication password
            from_email: Sender email address
        """
        self.w = WorkspaceClient()
        self.warehouse_id = warehouse_id
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = from_email

    def execute_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results.

        Args:
            sql_query: SQL query to execute

        Returns:
            List of dictionaries representing rows
        """
        print(f"Executing query on warehouse {self.warehouse_id}...")

        # Execute the statement
        statement = self.w.statement_execution.execute_statement(
            warehouse_id=self.warehouse_id,
            statement=sql_query,
            format=Format.JSON_ARRAY,
            disposition=Disposition.INLINE,
            wait_timeout="30s"
        )

        # Wait for completion
        if statement.status.state == StatementState.SUCCEEDED:
            print(f"Query executed successfully. Rows returned: {statement.result.row_count}")

            # Extract data
            if statement.result and statement.result.data_array:
                columns = [col.name for col in statement.manifest.schema.columns]
                rows = []

                for row_data in statement.result.data_array:
                    row_dict = dict(zip(columns, row_data))
                    rows.append(row_dict)

                return rows
            else:
                print("No data returned from query")
                return []
        else:
            error_msg = f"Query failed with state: {statement.status.state}"
            if statement.status.error:
                error_msg += f"\nError: {statement.status.error.message}"
            raise RuntimeError(error_msg)

    def create_pdf(
        self,
        data: List[Dict[str, Any]],
        output_path: str,
        title: str = "Dashboard Export",
        page_size: str = "LETTER",
        orientation: str = "landscape"
    ) -> str:
        """
        Create a PDF from query results.

        Args:
            data: List of dictionaries representing table rows
            output_path: Path to save the PDF file
            title: Title for the PDF document
            page_size: Page size (LETTER or A4)
            orientation: Page orientation (portrait or landscape)

        Returns:
            Path to the created PDF file
        """
        if not data:
            raise ValueError("No data to export to PDF")

        print(f"Creating PDF with {len(data)} rows...")

        # Determine page size
        if page_size.upper() == "A4":
            page = A4
        else:
            page = letter

        if orientation.lower() == "landscape":
            page = landscape(page)

        # Create PDF
        pdf = SimpleDocTemplate(
            output_path,
            pagesize=page,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch
        )

        # Container for elements
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            alignment=TA_CENTER
        )

        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER
        )

        # Add title
        elements.append(Paragraph(title, title_style))

        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elements.append(Paragraph(f"Generated: {timestamp}", subtitle_style))

        # Prepare table data
        columns = list(data[0].keys())
        table_data = [columns]  # Header row

        for row in data:
            table_data.append([str(row.get(col, '')) for col in columns])

        # Calculate column widths dynamically
        page_width = page[0] - 1*inch  # Account for margins
        col_width = page_width / len(columns)
        col_widths = [col_width] * len(columns)

        # Create table
        table = Table(table_data, colWidths=col_widths, repeatRows=1)

        # Style the table
        table_style = TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),

            # Body styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),

            # Alternating row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])

        table.setStyle(table_style)
        elements.append(table)

        # Add footer with row count
        elements.append(Spacer(1, 0.2*inch))
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        )
        elements.append(Paragraph(f"Total rows: {len(data)}", footer_style))

        # Build PDF
        pdf.build(elements)
        print(f"PDF created successfully: {output_path}")

        return output_path

    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        pdf_path: str,
        cc_emails: Optional[List[str]] = None
    ):
        """
        Send email with PDF attachment.

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body: Email body (plain text or HTML)
            pdf_path: Path to PDF file to attach
            cc_emails: Optional list of CC email addresses
        """
        print(f"Sending email to {', '.join(to_emails)}...")

        # Create message
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['To'] = ', '.join(to_emails)
        if cc_emails:
            msg['Cc'] = ', '.join(cc_emails)
        msg['Subject'] = subject

        # Add body
        msg.attach(MIMEText(body, 'plain'))

        # Attach PDF
        with open(pdf_path, 'rb') as f:
            pdf_attachment = MIMEApplication(f.read(), _subtype='pdf')
            pdf_attachment.add_header(
                'Content-Disposition',
                'attachment',
                filename=Path(pdf_path).name
            )
            msg.attach(pdf_attachment)

        # Send email
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)

                all_recipients = to_emails + (cc_emails or [])
                server.send_message(msg, self.from_email, all_recipients)

            print("Email sent successfully!")

        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            raise

    def export_and_email(
        self,
        sql_query: str,
        to_emails: List[str],
        subject: str,
        title: str = "Dashboard Export",
        output_dir: str = "./exports",
        page_size: str = "LETTER",
        orientation: str = "landscape",
        cc_emails: Optional[List[str]] = None
    ):
        """
        Complete workflow: Execute query, create PDF, and send email.

        Args:
            sql_query: SQL query to execute
            to_emails: List of recipient email addresses
            subject: Email subject
            title: Title for the PDF document
            output_dir: Directory to save PDF files
            page_size: Page size (LETTER or A4)
            orientation: Page orientation (portrait or landscape)
            cc_emails: Optional list of CC email addresses
        """
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"dashboard_export_{timestamp}.pdf"
        pdf_path = os.path.join(output_dir, pdf_filename)

        try:
            # Step 1: Execute query
            data = self.execute_query(sql_query)

            if not data:
                print("No data to export. Exiting.")
                return

            # Step 2: Create PDF
            self.create_pdf(
                data=data,
                output_path=pdf_path,
                title=title,
                page_size=page_size,
                orientation=orientation
            )

            # Step 3: Send email
            email_body = f"""
Hello,

Please find attached the dashboard export report: {title}

Report Details:
- Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- Total Rows: {len(data)}
- Columns: {len(data[0])}

This is an automated report generated from Databricks AI/BI Dashboard.

Best regards,
Databricks Export System
"""

            self.send_email(
                to_emails=to_emails,
                subject=subject,
                body=email_body,
                pdf_path=pdf_path,
                cc_emails=cc_emails
            )

            print(f"\n✓ Export complete! PDF saved to: {pdf_path}")

        except Exception as e:
            print(f"\n✗ Export failed: {str(e)}")
            raise


def main():
    """Main entry point for the script."""

    # Load configuration from environment variables
    WAREHOUSE_ID = os.getenv('DATABRICKS_WAREHOUSE_ID')
    SMTP_HOST = os.getenv('SMTP_HOST')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    FROM_EMAIL = os.getenv('FROM_EMAIL')

    # Validate required environment variables
    required_vars = {
        'DATABRICKS_WAREHOUSE_ID': WAREHOUSE_ID,
        'SMTP_HOST': SMTP_HOST,
        'SMTP_USER': SMTP_USER,
        'SMTP_PASSWORD': SMTP_PASSWORD,
        'FROM_EMAIL': FROM_EMAIL
    }

    missing_vars = [k for k, v in required_vars.items() if not v]
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your .env file or environment")
        sys.exit(1)

    # Initialize exporter
    exporter = DashboardExporter(
        warehouse_id=WAREHOUSE_ID,
        smtp_host=SMTP_HOST,
        smtp_port=SMTP_PORT,
        smtp_user=SMTP_USER,
        smtp_password=SMTP_PASSWORD,
        from_email=FROM_EMAIL
    )

    # Example usage - customize these values
    SQL_QUERY = """
    SELECT *
    FROM your_catalog.your_schema.your_dashboard_table
    LIMIT 1000
    """

    TO_EMAILS = ['recipient@example.com']
    CC_EMAILS = []  # Optional
    SUBJECT = 'Dashboard Export Report - ' + datetime.now().strftime("%Y-%m-%d")
    TITLE = 'AI/BI Dashboard Export'

    # Run the export
    exporter.export_and_email(
        sql_query=SQL_QUERY,
        to_emails=TO_EMAILS,
        subject=SUBJECT,
        title=TITLE,
        cc_emails=CC_EMAILS,
        page_size="LETTER",
        orientation="landscape"
    )


if __name__ == "__main__":
    main()
