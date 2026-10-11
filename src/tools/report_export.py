"""
Report Exporters: Generates downloadable Markdown and formatted PDF analytical reports.
"""
from pathlib import Path
from typing import Any, Optional
from config.settings import settings

class ReportExporter:
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or settings.reports_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_markdown(self, report_text: str, filename: str = "analytical_report.md") -> Path:
        out_path = self.output_dir / filename
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        return out_path

    def export_pdf(self, title: str, report_text: str, filename: str = "analytical_report.pdf") -> Path:
        out_path = self.output_dir / filename
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            doc = SimpleDocTemplate(
                str(out_path),
                pagesize=letter,
                rightMargin=40, leftMargin=40,
                topMargin=40, bottomMargin=40
            )
            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                "DocTitle",
                parent=styles["Title"],
                fontSize=20,
                leading=24,
                textColor=colors.HexColor("#1e293b"),
                spaceAfter=14
            )
            h2_style = ParagraphStyle(
                "DocH2",
                parent=styles["Heading2"],
                fontSize=14,
                leading=18,
                textColor=colors.HexColor("#0f172a"),
                spaceBefore=10,
                spaceAfter=6
            )
            body_style = ParagraphStyle(
                "DocBody",
                parent=styles["Normal"],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor("#334155"),
                spaceAfter=6
            )

            story = [
                Paragraph(title, title_style),
                Spacer(1, 10)
            ]

            lines = report_text.split("\n")
            for line in lines:
                clean_line = line.strip()
                if not clean_line:
                    story.append(Spacer(1, 4))
                elif clean_line.startswith("# "):
                    story.append(Paragraph(clean_line[2:], title_style))
                elif clean_line.startswith("## "):
                    story.append(Paragraph(clean_line[3:], h2_style))
                elif clean_line.startswith("### "):
                    story.append(Paragraph(clean_line[4:], h2_style))
                else:
                    # Escape basic html entities for ReportLab XML parser
                    escaped = clean_line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    story.append(Paragraph(escaped, body_style))

            doc.build(story)
            return out_path
        except Exception:
            # Fallback: create markdown file with .pdf.txt note if PDF build fails
            fallback_path = self.output_dir / f"{filename}.txt"
            with open(fallback_path, "w", encoding="utf-8") as f:
                f.write(report_text)
            return fallback_path
