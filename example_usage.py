#!/usr/bin/env python3
"""
Example usage scripts for the Dashboard Export Tool

This file contains several practical examples of how to use the DashboardExporter class.
"""

import os
from datetime import datetime, timedelta
from export_dashboard import DashboardExporter


def example_1_simple_export():
    """
    Example 1: Simple dashboard export
    Export a table and send it to one recipient.
    """
    print("\n=== Example 1: Simple Export ===")

    exporter = DashboardExporter(
        warehouse_id=os.getenv('DATABRICKS_WAREHOUSE_ID'),
        smtp_host=os.getenv('SMTP_HOST'),
        smtp_port=int(os.getenv('SMTP_PORT', '587')),
        smtp_user=os.getenv('SMTP_USER'),
        smtp_password=os.getenv('SMTP_PASSWORD'),
        from_email=os.getenv('FROM_EMAIL')
    )

    SQL_QUERY = """
    SELECT
        'Product A' as product,
        100 as quantity,
        1500.00 as revenue
    UNION ALL
    SELECT 'Product B', 85, 1200.00
    UNION ALL
    SELECT 'Product C', 120, 2400.00
    """

    exporter.export_and_email(
        sql_query=SQL_QUERY,
        to_emails=['recipient@example.com'],
        subject='Simple Dashboard Export',
        title='Product Sales Summary'
    )


def example_2_daily_sales_report():
    """
    Example 2: Daily Sales Report
    Export yesterday's sales data with professional formatting.
    """
    print("\n=== Example 2: Daily Sales Report ===")

    exporter = DashboardExporter(
        warehouse_id=os.getenv('DATABRICKS_WAREHOUSE_ID'),
        smtp_host=os.getenv('SMTP_HOST'),
        smtp_port=int(os.getenv('SMTP_PORT', '587')),
        smtp_user=os.getenv('SMTP_USER'),
        smtp_password=os.getenv('SMTP_PASSWORD'),
        from_email=os.getenv('FROM_EMAIL')
    )

    # Query for yesterday's sales
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    SQL_QUERY = f"""
    SELECT
        date,
        region,
        product_category,
        total_sales,
        order_count,
        avg_order_value
    FROM sales.daily_summary
    WHERE date = '{yesterday}'
    ORDER BY total_sales DESC
    """

    exporter.export_and_email(
        sql_query=SQL_QUERY,
        to_emails=['sales-team@company.com'],
        subject=f'Daily Sales Report - {yesterday}',
        title='Daily Sales Performance',
        cc_emails=['manager@company.com'],
        page_size='LETTER',
        orientation='landscape'
    )


def example_3_custom_pdf_only():
    """
    Example 3: Create PDF without sending email
    Generate a PDF file for manual distribution.
    """
    print("\n=== Example 3: PDF Only (No Email) ===")

    exporter = DashboardExporter(
        warehouse_id=os.getenv('DATABRICKS_WAREHOUSE_ID'),
        smtp_host=os.getenv('SMTP_HOST'),
        smtp_port=int(os.getenv('SMTP_PORT', '587')),
        smtp_user=os.getenv('SMTP_USER'),
        smtp_password=os.getenv('SMTP_PASSWORD'),
        from_email=os.getenv('FROM_EMAIL')
    )

    SQL_QUERY = """
    SELECT
        customer_name,
        account_balance,
        last_transaction_date,
        status
    FROM finance.customer_accounts
    WHERE account_balance > 10000
    ORDER BY account_balance DESC
    LIMIT 50
    """

    # Execute query
    data = exporter.execute_query(SQL_QUERY)

    # Create PDF only
    pdf_path = exporter.create_pdf(
        data=data,
        output_path='./exports/high_value_customers.pdf',
        title='High Value Customers Report',
        page_size='A4',
        orientation='portrait'
    )

    print(f"PDF created: {pdf_path}")


def example_4_weekly_summary():
    """
    Example 4: Weekly Summary Report
    Aggregate data for the past week and send to multiple recipients.
    """
    print("\n=== Example 4: Weekly Summary ===")

    exporter = DashboardExporter(
        warehouse_id=os.getenv('DATABRICKS_WAREHOUSE_ID'),
        smtp_host=os.getenv('SMTP_HOST'),
        smtp_port=int(os.getenv('SMTP_PORT', '587')),
        smtp_user=os.getenv('SMTP_USER'),
        smtp_password=os.getenv('SMTP_PASSWORD'),
        from_email=os.getenv('FROM_EMAIL')
    )

    SQL_QUERY = """
    SELECT
        week_start,
        department,
        total_hours,
        projects_completed,
        team_size,
        avg_productivity_score
    FROM operations.weekly_metrics
    WHERE week_start = date_trunc('week', current_date() - 7)
    ORDER BY department
    """

    exporter.export_and_email(
        sql_query=SQL_QUERY,
        to_emails=[
            'team-leads@company.com',
            'operations@company.com'
        ],
        subject=f'Weekly Operations Summary - Week of {datetime.now().strftime("%Y-%m-%d")}',
        title='Weekly Operations Metrics',
        cc_emails=['ceo@company.com'],
        page_size='LETTER',
        orientation='landscape'
    )


def example_5_large_dataset():
    """
    Example 5: Large Dataset Export
    Handle large query results efficiently.
    """
    print("\n=== Example 5: Large Dataset Export ===")

    exporter = DashboardExporter(
        warehouse_id=os.getenv('DATABRICKS_WAREHOUSE_ID'),
        smtp_host=os.getenv('SMTP_HOST'),
        smtp_port=int(os.getenv('SMTP_PORT', '587')),
        smtp_user=os.getenv('SMTP_USER'),
        smtp_password=os.getenv('SMTP_PASSWORD'),
        from_email=os.getenv('FROM_EMAIL')
    )

    # Query with LIMIT to manage size
    SQL_QUERY = """
    SELECT
        transaction_id,
        customer_id,
        transaction_date,
        amount,
        payment_method,
        status
    FROM transactions.all_transactions
    WHERE transaction_date >= current_date() - 30
    ORDER BY transaction_date DESC
    LIMIT 5000
    """

    exporter.export_and_email(
        sql_query=SQL_QUERY,
        to_emails=['finance@company.com'],
        subject='30-Day Transaction Report (Top 5000)',
        title='Recent Transactions - Last 30 Days',
        page_size='A4',
        orientation='landscape'
    )


def example_6_conditional_export():
    """
    Example 6: Conditional Export
    Only send email if data meets certain criteria.
    """
    print("\n=== Example 6: Conditional Export ===")

    exporter = DashboardExporter(
        warehouse_id=os.getenv('DATABRICKS_WAREHOUSE_ID'),
        smtp_host=os.getenv('SMTP_HOST'),
        smtp_port=int(os.getenv('SMTP_PORT', '587')),
        smtp_user=os.getenv('SMTP_USER'),
        smtp_password=os.getenv('SMTP_PASSWORD'),
        from_email=os.getenv('FROM_EMAIL')
    )

    # Query for high-priority alerts
    SQL_QUERY = """
    SELECT
        alert_id,
        alert_type,
        severity,
        affected_systems,
        timestamp,
        description
    FROM monitoring.active_alerts
    WHERE severity IN ('HIGH', 'CRITICAL')
    AND status = 'OPEN'
    ORDER BY timestamp DESC
    """

    # Execute query
    data = exporter.execute_query(SQL_QUERY)

    # Only send email if there are critical alerts
    if len(data) > 0:
        print(f"Found {len(data)} critical alerts. Sending notification...")

        exporter.export_and_email(
            sql_query=SQL_QUERY,
            to_emails=['oncall@company.com'],
            subject=f'ALERT: {len(data)} Critical System Alerts Detected',
            title='Critical System Alerts',
            cc_emails=['devops@company.com']
        )
    else:
        print("No critical alerts found. Skipping email.")


def example_7_multiple_queries():
    """
    Example 7: Multiple Queries in One PDF
    Execute multiple queries and combine results in a single report.
    """
    print("\n=== Example 7: Multiple Queries Combined ===")

    exporter = DashboardExporter(
        warehouse_id=os.getenv('DATABRICKS_WAREHOUSE_ID'),
        smtp_host=os.getenv('SMTP_HOST'),
        smtp_port=int(os.getenv('SMTP_PORT', '587')),
        smtp_user=os.getenv('SMTP_USER'),
        smtp_password=os.getenv('SMTP_PASSWORD'),
        from_email=os.getenv('FROM_EMAIL')
    )

    # Query 1: Top products
    query1_data = exporter.execute_query("""
        SELECT product_name, total_sales
        FROM products.summary
        ORDER BY total_sales DESC
        LIMIT 10
    """)

    # Query 2: Regional performance
    query2_data = exporter.execute_query("""
        SELECT region, revenue, growth_rate
        FROM regions.performance
        ORDER BY revenue DESC
    """)

    # Note: This example shows the pattern, but you'd need to modify
    # create_pdf to handle multiple datasets. For now, use one query.
    print("Tip: To combine multiple queries, execute them separately")
    print("and merge the data before calling create_pdf()")


def example_8_scheduled_export():
    """
    Example 8: Scheduled Export Template
    Template for use with cron jobs or task schedulers.
    """
    print("\n=== Example 8: Scheduled Export Template ===")

    try:
        exporter = DashboardExporter(
            warehouse_id=os.getenv('DATABRICKS_WAREHOUSE_ID'),
            smtp_host=os.getenv('SMTP_HOST'),
            smtp_port=int(os.getenv('SMTP_PORT', '587')),
            smtp_user=os.getenv('SMTP_USER'),
            smtp_password=os.getenv('SMTP_PASSWORD'),
            from_email=os.getenv('FROM_EMAIL')
        )

        # Determine report period based on current day
        today = datetime.now()
        report_date = today.strftime('%Y-%m-%d')

        SQL_QUERY = f"""
        SELECT
            metric_name,
            metric_value,
            target_value,
            variance_percent
        FROM kpis.daily_metrics
        WHERE report_date = '{report_date}'
        ORDER BY metric_name
        """

        exporter.export_and_email(
            sql_query=SQL_QUERY,
            to_emails=['kpi-report@company.com'],
            subject=f'Daily KPI Report - {report_date}',
            title=f'Daily Key Performance Indicators - {report_date}',
            page_size='LETTER',
            orientation='portrait'
        )

        print(f"Scheduled export completed successfully at {today}")

    except Exception as e:
        print(f"Scheduled export failed: {str(e)}")
        # In production, log this error or send alert
        raise


if __name__ == "__main__":
    """
    Run examples. Uncomment the examples you want to test.
    """

    print("Dashboard Export Tool - Example Usage")
    print("=" * 50)

    # Make sure environment variables are set
    from dotenv import load_dotenv
    load_dotenv()

    required_vars = [
        'DATABRICKS_WAREHOUSE_ID',
        'SMTP_HOST',
        'SMTP_USER',
        'SMTP_PASSWORD',
        'FROM_EMAIL'
    ]

    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        print(f"\nError: Missing environment variables: {', '.join(missing)}")
        print("Please configure your .env file before running examples.")
        exit(1)

    # Uncomment the examples you want to run:

    # example_1_simple_export()
    # example_2_daily_sales_report()
    # example_3_custom_pdf_only()
    # example_4_weekly_summary()
    # example_5_large_dataset()
    # example_6_conditional_export()
    # example_7_multiple_queries()
    # example_8_scheduled_export()

    print("\nNote: All examples are commented out by default.")
    print("Edit this file to uncomment and run specific examples.")
