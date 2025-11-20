"""
Configuration module for Dashboard Export Tool

This module provides configuration management using environment variables.
"""

import os
from dataclasses import dataclass
from typing import List, Optional
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()


@dataclass
class DatabricksConfig:
    """Databricks configuration."""
    warehouse_id: str
    host: Optional[str] = None
    token: Optional[str] = None

    @classmethod
    def from_env(cls) -> 'DatabricksConfig':
        """Load Databricks configuration from environment variables."""
        return cls(
            warehouse_id=os.getenv('DATABRICKS_WAREHOUSE_ID', ''),
            host=os.getenv('DATABRICKS_HOST'),
            token=os.getenv('DATABRICKS_TOKEN')
        )


@dataclass
class SMTPConfig:
    """SMTP email configuration."""
    host: str
    port: int
    user: str
    password: str
    from_email: str
    use_tls: bool = True

    @classmethod
    def from_env(cls) -> 'SMTPConfig':
        """Load SMTP configuration from environment variables."""
        return cls(
            host=os.getenv('SMTP_HOST', ''),
            port=int(os.getenv('SMTP_PORT', '587')),
            user=os.getenv('SMTP_USER', ''),
            password=os.getenv('SMTP_PASSWORD', ''),
            from_email=os.getenv('FROM_EMAIL', ''),
            use_tls=os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        )


@dataclass
class ExportConfig:
    """Export configuration."""
    output_dir: str = './exports'
    page_size: str = 'LETTER'  # LETTER or A4
    orientation: str = 'landscape'  # landscape or portrait
    max_rows: int = 10000

    @classmethod
    def from_env(cls) -> 'ExportConfig':
        """Load export configuration from environment variables."""
        return cls(
            output_dir=os.getenv('EXPORT_OUTPUT_DIR', './exports'),
            page_size=os.getenv('EXPORT_PAGE_SIZE', 'LETTER'),
            orientation=os.getenv('EXPORT_ORIENTATION', 'landscape'),
            max_rows=int(os.getenv('EXPORT_MAX_ROWS', '10000'))
        )


@dataclass
class AppConfig:
    """Complete application configuration."""
    databricks: DatabricksConfig
    smtp: SMTPConfig
    export: ExportConfig

    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Load complete application configuration from environment variables."""
        return cls(
            databricks=DatabricksConfig.from_env(),
            smtp=SMTPConfig.from_env(),
            export=ExportConfig.from_env()
        )

    def validate(self) -> List[str]:
        """
        Validate configuration and return list of errors.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Validate Databricks config
        if not self.databricks.warehouse_id:
            errors.append("DATABRICKS_WAREHOUSE_ID is required")

        # Validate SMTP config
        if not self.smtp.host:
            errors.append("SMTP_HOST is required")
        if not self.smtp.user:
            errors.append("SMTP_USER is required")
        if not self.smtp.password:
            errors.append("SMTP_PASSWORD is required")
        if not self.smtp.from_email:
            errors.append("FROM_EMAIL is required")

        # Validate export config
        if self.export.page_size not in ['LETTER', 'A4']:
            errors.append(f"Invalid EXPORT_PAGE_SIZE: {self.export.page_size} (must be LETTER or A4)")
        if self.export.orientation not in ['landscape', 'portrait']:
            errors.append(f"Invalid EXPORT_ORIENTATION: {self.export.orientation} (must be landscape or portrait)")

        return errors


# Example configuration presets
GMAIL_SMTP_CONFIG = {
    'SMTP_HOST': 'smtp.gmail.com',
    'SMTP_PORT': '587',
    'SMTP_USE_TLS': 'true'
}

OUTLOOK_SMTP_CONFIG = {
    'SMTP_HOST': 'smtp-mail.outlook.com',
    'SMTP_PORT': '587',
    'SMTP_USE_TLS': 'true'
}

OFFICE365_SMTP_CONFIG = {
    'SMTP_HOST': 'smtp.office365.com',
    'SMTP_PORT': '587',
    'SMTP_USE_TLS': 'true'
}
