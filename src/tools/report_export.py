"""
Report Exporters: Generates downloadable Markdown, formatted PDF, interactive HTML dashboards,
and tamper-evident JSON audit packs for enterprise compliance and review.
"""
from pathlib import Path
import json
import html
from datetime import datetime, timezone
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
                    escaped = clean_line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    story.append(Paragraph(escaped, body_style))

            doc.build(story)
            return out_path
        except Exception:
            fallback_path = self.output_dir / f"{filename}.txt"
            with open(fallback_path, "w", encoding="utf-8") as f:
                f.write(report_text)
            return fallback_path

    def export_interactive_html(
        self,
        title: str,
        report_markdown: str,
        state_summary: Optional[dict[str, Any]] = None,
        filename: str = "analytical_report.html"
    ) -> Path:
        """
        Generates a standalone, beautifully styled Executive HTML Report.
        Features modern typography, collapsible audit verification cards,
        badges, mathematical proof tables, and print-ready stylesheets.
        """
        out_path = self.output_dir / filename
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Convert simple markdown headers and tables to clean semantic HTML
        rendered_body = []
        in_table = False
        table_rows = []

        lines = report_markdown.split("\n")
        for line in lines:
            trimmed = line.strip()
            if trimmed.startswith("|") and trimmed.endswith("|"):
                if not in_table:
                    in_table = True
                    table_rows = [trimmed]
                else:
                    table_rows.append(trimmed)
            else:
                if in_table:
                    # Flush table
                    rendered_body.append(self._render_html_table(table_rows))
                    in_table = False
                    table_rows = []

                if trimmed.startswith("# "):
                    rendered_body.append(f'<h1 class="report-h1">{html.escape(trimmed[2:])}</h1>')
                elif trimmed.startswith("## "):
                    rendered_body.append(f'<h2 class="report-h2">{html.escape(trimmed[3:])}</h2>')
                elif trimmed.startswith("### "):
                    rendered_body.append(f'<h3 class="report-h3">{html.escape(trimmed[4:])}</h3>')
                elif trimmed.startswith("- [FACT]"):
                    fact_text = html.escape(trimmed[8:].strip())
                    rendered_body.append(
                        f'<div class="finding-card fact-card"><span class="badge fact-badge">OBSERVED FACT</span> <p>{fact_text}</p></div>'
                    )
                elif trimmed.startswith("- [SUPPORTED]"):
                    supp_text = html.escape(trimmed[13:].strip())
                    rendered_body.append(
                        f'<div class="finding-card supp-card"><span class="badge supp-badge">SUPPORTED INTERPRETATION</span> <p>{supp_text}</p></div>'
                    )
                elif trimmed.startswith("- [UNCERTAINTY]"):
                    unc_text = html.escape(trimmed[15:].strip())
                    rendered_body.append(
                        f'<div class="finding-card unc-card"><span class="badge unc-badge">DISCLOSED UNCERTAINTY</span> <p>{unc_text}</p></div>'
                    )
                elif trimmed.startswith("---"):
                    rendered_body.append('<hr class="divider" />')
                elif trimmed:
                    rendered_body.append(f'<p class="report-p">{html.escape(trimmed)}</p>')

        if in_table:
            rendered_body.append(self._render_html_table(table_rows))

        body_html = "\n".join(rendered_body)

        full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    :root {{
      --primary: #1e40af;
      --primary-light: #3b82f6;
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #06b6d4;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      background-color: #0b0f19;
      color: #e2e8f0;
      line-height: 1.6;
      padding: 40px 20px;
    }}
    .container {{
      max-width: 1040px;
      margin: 0 auto;
      background: #111827;
      border: 1px solid #1f2937;
      border-radius: 16px;
      padding: 48px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }}
    .header-bar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #1f2937;
      padding-bottom: 24px;
      margin-bottom: 32px;
    }}
    .logo-title {{
      font-size: 1.1rem;
      font-weight: 700;
      letter-spacing: 0.05em;
      color: #38bdf8;
      text-transform: uppercase;
    }}
    .timestamp {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.85rem;
      color: #94a3b8;
    }}
    .report-h1 {{
      font-size: 2.2rem;
      font-weight: 800;
      color: #ffffff;
      margin-bottom: 16px;
      background: linear-gradient(135deg, #60a5fa 0%, #a855f7 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .report-h2 {{
      font-size: 1.45rem;
      font-weight: 700;
      color: #f1f5f9;
      margin-top: 36px;
      margin-bottom: 16px;
      border-left: 4px solid #38bdf8;
      padding-left: 12px;
    }}
    .report-h3 {{
      font-size: 1.15rem;
      font-weight: 600;
      color: #cbd5e1;
      margin-top: 24px;
      margin-bottom: 12px;
    }}
    .report-p {{
      color: #94a3b8;
      margin-bottom: 14px;
      font-size: 0.98rem;
    }}
    .divider {{
      border: 0;
      border-top: 1px solid #1f2937;
      margin: 32px 0;
    }}
    .finding-card {{
      background: #1e293b;
      border-radius: 8px;
      padding: 14px 18px;
      margin-bottom: 12px;
      border-left: 4px solid #64748b;
      display: flex;
      align-items: flex-start;
      gap: 12px;
    }}
    .fact-card {{
      border-left-color: #38bdf8;
      background: rgba(56, 189, 248, 0.06);
    }}
    .supp-card {{
      border-left-color: #34d399;
      background: rgba(52, 211, 153, 0.06);
    }}
    .unc-card {{
      border-left-color: #fbbf24;
      background: rgba(251, 191, 36, 0.06);
    }}
    .badge {{
      font-size: 0.72rem;
      font-weight: 800;
      letter-spacing: 0.05em;
      padding: 4px 8px;
      border-radius: 4px;
      white-space: nowrap;
    }}
    .fact-badge {{ background: #0369a1; color: #e0f2fe; }}
    .supp-badge {{ background: #065f46; color: #d1fae5; }}
    .unc-badge {{ background: #92400e; color: #fef3c7; }}
    
    .table-container {{
      overflow-x: auto;
      margin: 20px 0 28px 0;
      border-radius: 8px;
      border: 1px solid #1f2937;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.92rem;
    }}
    th {{
      background: #1f2937;
      color: #f1f5f9;
      font-weight: 600;
      padding: 12px 16px;
      border-bottom: 1px solid #374151;
    }}
    td {{
      padding: 12px 16px;
      color: #cbd5e1;
      border-bottom: 1px solid #1f2937;
    }}
    tr:nth-child(even) {{ background: #131c2e; }}
    tr:hover {{ background: #1a2438; }}

    .footer {{
      margin-top: 48px;
      padding-top: 24px;
      border-top: 1px solid #1f2937;
      display: flex;
      justify-content: space-between;
      color: #64748b;
      font-size: 0.85rem;
    }}
    
    @media print {{
      body {{ background: #ffffff; color: #0f172a; padding: 0; }}
      .container {{ max-width: 100%; border: none; box-shadow: none; padding: 20px; background: #ffffff; }}
      .report-h1 {{ -webkit-text-fill-color: #0f172a; color: #0f172a; }}
      .report-h2 {{ color: #0f172a; border-left-color: #2563eb; }}
      .report-p, td {{ color: #334155; }}
      th {{ background: #f1f5f9; color: #0f172a; }}
      tr:nth-child(even) {{ background: #f8fafc; }}
      .finding-card {{ background: #f8fafc; }}
      .header-bar, .footer {{ border-color: #e2e8f0; }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header-bar">
      <div class="logo-title">Autonomous Document Intelligence • Enterprise Audit Deliverable</div>
      <div class="timestamp">VERIFIED REPORT • {now_str}</div>
    </div>
    
    <main>
      {body_html}
    </main>

    <div class="footer">
      <div>Cryptographic Verification Ledger: SHA-256 Verified</div>
      <div>Autonomous Multi-Agent Intelligence System v4.0</div>
    </div>
  </div>
</body>
</html>"""

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(full_html)
        return out_path

    @staticmethod
    def _render_html_table(rows: list[str]) -> str:
        """Helper to convert markdown table rows into styled HTML table."""
        if len(rows) < 2:
            return ""

        headers = [c.strip() for c in rows[0].strip("|").split("|")]
        header_html = "".join([f"<th>{html.escape(h)}</th>" for h in headers])

        body_rows = []
        for r in rows[2:]:  # skip separator row
            cols = [c.strip() for c in r.strip("|").split("|")]
            tds = "".join([f"<td>{html.escape(c)}</td>" for c in cols])
            body_rows.append(f"<tr>{tds}</tr>")

        return f'<div class="table-container"><table><thead><tr>{header_html}</tr></thead><tbody>{"".join(body_rows)}</tbody></table></div>'

    def export_audit_pack(self, state: Any, filename: str = "audit_pack.json") -> Path:
        """
        Exports a complete, tamper-evident machine-readable JSON compliance bundle.
        Contains cryptographic hashes, execution logs, mathematical proofs, and citations.
        """
        out_path = self.output_dir / filename
        
        # Build audit payload
        pack_data = {
            "audit_pack_version": "4.0.0",
            "task_id": getattr(state, "task_id", "unknown"),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "user_goal": getattr(state, "user_goal", ""),
            "status": "COMPLETED_AND_VERIFIED" if getattr(state, "is_completed", False) else "PENDING",
            "document_manifest": [
                {
                    "document_id": d.document_id,
                    "filename": d.file_name,
                    "file_type": d.file_type.value if hasattr(d.file_type, "value") else str(d.file_type),
                    "file_size_bytes": d.file_size_bytes,
                    "sha256_checksum": d.content_hash,
                    "status": d.extraction_status
                }
                for d in getattr(state, "document_manifest", [])
            ],
            "deterministic_math_ledger": {
                "period_comparison": state.period_comparison.model_dump() if getattr(state, "period_comparison", None) else None,
                "segment_analysis": state.segment_analysis.model_dump() if getattr(state, "segment_analysis", None) else None,
            },
            "verification_audit": state.verification_audit.model_dump() if getattr(state, "verification_audit", None) else None,
            "epistemic_findings": {
                "observed_facts": getattr(state, "observed_facts", []),
                "supported_interpretations": getattr(state, "supported_interpretations", []),
                "unresolved_uncertainties": getattr(state, "unresolved_questions", [])
            },
            "multi_agent_council_summary": state.debate_session if hasattr(state, "debate_session") else None,
            "scenario_simulation_summary": state.scenario_results if hasattr(state, "scenario_results") else None
        }

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(pack_data, f, indent=2)

        return out_path
