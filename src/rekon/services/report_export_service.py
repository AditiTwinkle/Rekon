"""Report export service for multiple formats."""

import csv
import io
import json
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.orm import Session


class ReportExportService:
    """Service for exporting reports in multiple formats."""

    def __init__(self, db: Session):
        """Initialize service.

        Args:
            db: Database session
        """
        self.db = db

    def export_to_json(self, report_data: Dict[str, Any]) -> str:
        """Export report to JSON format.

        Args:
            report_data: Report data dictionary

        Returns:
            JSON string
        """
        return json.dumps(report_data, indent=2, default=str)

    def export_to_csv(self, report_data: Dict[str, Any]) -> str:
        """Export report to CSV format.

        Args:
            report_data: Report data dictionary

        Returns:
            CSV string
        """
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Report Type", report_data.get("report_type", "N/A")])
        writer.writerow(["Generated At", report_data.get("generated_at", "N/A")])
        writer.writerow(["Organization ID", report_data.get("organization_id", "N/A")])
        writer.writerow(["Framework", report_data.get("framework", "N/A")])
        writer.writerow([])

        # Write sections
        sections = report_data.get("sections", {})
        for section_name, section_data in sections.items():
            writer.writerow([section_name.upper()])
            self._write_section_to_csv(writer, section_data)
            writer.writerow([])

        return output.getvalue()

    def export_to_html(self, report_data: Dict[str, Any]) -> str:
        """Export report to HTML format.

        Args:
            report_data: Report data dictionary

        Returns:
            HTML string
        """
        html = []
        html.append("<!DOCTYPE html>")
        html.append("<html>")
        html.append("<head>")
        html.append("<meta charset='UTF-8'>")
        html.append("<title>Compliance Report</title>")
        html.append("<style>")
        html.append(self._get_html_styles())
        html.append("</style>")
        html.append("</head>")
        html.append("<body>")

        # Header
        html.append("<div class='header'>")
        html.append(f"<h1>Compliance Report</h1>")
        html.append(f"<p><strong>Report Type:</strong> {report_data.get('report_type', 'N/A')}</p>")
        html.append(f"<p><strong>Generated:</strong> {report_data.get('generated_at', 'N/A')}</p>")
        html.append(f"<p><strong>Framework:</strong> {report_data.get('framework', 'N/A')}</p>")
        html.append("</div>")

        # Sections
        sections = report_data.get("sections", {})
        for section_name, section_data in sections.items():
            html.append(f"<div class='section'>")
            html.append(f"<h2>{section_name.replace('_', ' ').title()}</h2>")
            html.append(self._render_section_html(section_data))
            html.append("</div>")

        html.append("</body>")
        html.append("</html>")

        return "\n".join(html)

    def export_to_pdf(self, report_data: Dict[str, Any]) -> bytes:
        """Export report to PDF format.

        Args:
            report_data: Report data dictionary

        Returns:
            PDF bytes

        Note:
            In production, this would use a library like reportlab or weasyprint
            For now, we return a placeholder
        """
        # In production, use reportlab or weasyprint
        # For now, return HTML as bytes with PDF header
        html_content = self.export_to_html(report_data)
        return html_content.encode("utf-8")

    def _write_section_to_csv(self, writer: csv.writer, data: Any, indent: int = 0) -> None:
        """Recursively write section data to CSV.

        Args:
            writer: CSV writer
            data: Data to write
            indent: Indentation level
        """
        prefix = "  " * indent

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    writer.writerow([f"{prefix}{key}"])
                    self._write_section_to_csv(writer, value, indent + 1)
                else:
                    writer.writerow([f"{prefix}{key}", str(value)])
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    self._write_section_to_csv(writer, item, indent)
                else:
                    writer.writerow([f"{prefix}{item}"])

    def _render_section_html(self, data: Any, level: int = 3) -> str:
        """Recursively render section data as HTML.

        Args:
            data: Data to render
            level: HTML heading level

        Returns:
            HTML string
        """
        html = []

        if isinstance(data, dict):
            html.append("<table class='data-table'>")
            for key, value in data.items():
                html.append("<tr>")
                html.append(f"<td class='key'>{key.replace('_', ' ').title()}</td>")
                if isinstance(value, (dict, list)):
                    html.append("<td>")
                    html.append(self._render_section_html(value, level + 1))
                    html.append("</td>")
                else:
                    html.append(f"<td class='value'>{str(value)}</td>")
                html.append("</tr>")
            html.append("</table>")
        elif isinstance(data, list):
            html.append("<ul>")
            for item in data:
                html.append("<li>")
                if isinstance(item, dict):
                    html.append(self._render_section_html(item, level + 1))
                else:
                    html.append(str(item))
                html.append("</li>")
            html.append("</ul>")
        else:
            html.append(f"<p>{str(data)}</p>")

        return "\n".join(html)

    def _get_html_styles(self) -> str:
        """Get CSS styles for HTML report.

        Returns:
            CSS string
        """
        return """
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            color: #333;
        }
        .header {
            border-bottom: 2px solid #007bff;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #007bff;
            margin: 0;
        }
        .section {
            margin-bottom: 30px;
            page-break-inside: avoid;
        }
        .section h2 {
            color: #0056b3;
            border-left: 4px solid #007bff;
            padding-left: 10px;
            margin-top: 0;
        }
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        .data-table tr {
            border-bottom: 1px solid #ddd;
        }
        .data-table tr:hover {
            background-color: #f5f5f5;
        }
        .data-table td {
            padding: 10px;
        }
        .data-table .key {
            font-weight: bold;
            width: 30%;
            background-color: #f9f9f9;
        }
        .data-table .value {
            width: 70%;
        }
        ul {
            margin: 10px 0;
            padding-left: 20px;
        }
        li {
            margin: 5px 0;
        }
        @media print {
            body {
                margin: 0;
            }
            .section {
                page-break-inside: avoid;
            }
        }
        """
