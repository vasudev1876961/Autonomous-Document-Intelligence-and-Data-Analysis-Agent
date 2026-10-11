"""
Generates representative sample evaluation documents:
- Quarterly_Report.pdf (using reportlab)
- Revenue_Data.xlsx (using openpyxl)
- Segment_Performance.csv (using pandas)
- Conflicting_Report.pdf (with deliberate discrepancy for testing reconciliation)
"""
from pathlib import Path
import pandas as pd
import openpyxl
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_samples(target_dir: Path):
    target_dir.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()

    # 1. Quarterly_Report.pdf
    pdf_path = target_dir / "Quarterly_Report.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    story = [
        Paragraph("Corporate Quarterly Executive Performance Report", styles["Title"]),
        Spacer(1, 14),
        Paragraph("<b>Reporting Periods:</b> Q1 to Q2 (All currency figures in ₹ lakh)", styles["Normal"]),
        Spacer(1, 10),
        Paragraph("<b>1. Executive Performance Overview:</b>", styles["Heading2"]),
        Paragraph(
            "During the second quarter (Q2), consolidated revenue declined from ₹1,000 lakh in Q1 to ₹900 lakh, "
            "representing an absolute decline of ₹100 lakh (-10.0%). Performance across operational business segments "
            "diverged significantly during this comparative window.",
            styles["Normal"]
        ),
        Spacer(1, 10),
        Paragraph("<b>2. Segment Analysis & Operational Factors:</b>", styles["Heading2"]),
        Paragraph(
            "<b>Segment A:</b> Segment A recorded a contraction in revenue from ₹500 lakh to ₹420 lakh (a net decline of ₹80 lakh). "
            "The operational investigation documents lower order volumes for Segment A caused by supply chain realignment "
            "and seasonal procurement delays from enterprise tier-1 customers.",
            styles["Normal"]
        ),
        Spacer(1, 8),
        Paragraph(
            "<b>Segment B:</b> Segment B revenue softened from ₹300 lakh to ₹280 lakh (a net decline of ₹20 lakh). "
            "Specific explanatory details and market drivers for Segment B remain under operational review.",
            styles["Normal"]
        ),
        Spacer(1, 8),
        Paragraph(
            "<b>Segment C:</b> Segment C maintained flat performance, generating ₹200 lakh in both Q1 and Q2.",
            styles["Normal"]
        ),
    ]
    doc.build(story)
    print(f"Generated {pdf_path.name}")

    # 2. Revenue_Data.xlsx
    xlsx_path = target_dir / "Revenue_Data.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Revenue"
    ws.append(["Segment", "Q1", "Q2", "Unit"])
    ws.append(["Segment A", 500, 420, "₹ lakh"])
    ws.append(["Segment B", 300, 280, "₹ lakh"])
    ws.append(["Segment C", 200, 200, "₹ lakh"])
    ws.append(["Total", 1000, 900, "₹ lakh"])
    wb.save(str(xlsx_path))
    print(f"Generated {xlsx_path.name}")

    # 3. Segment_Performance.csv
    csv_path = target_dir / "Segment_Performance.csv"
    df = pd.DataFrame([
        {"Segment": "Segment A", "Q1": 500, "Q2": 420, "Category": "Hardware", "Region": "Domestic"},
        {"Segment": "Segment B", "Q1": 300, "Q2": 280, "Category": "Services", "Region": "Export"},
        {"Segment": "Segment C", "Q1": 200, "Q2": 200, "Category": "Subscriptions", "Region": "Global"},
    ])
    df.to_csv(csv_path, index=False)
    print(f"Generated {csv_path.name}")

    # 4. Conflicting_Report.pdf (deliberate 905 lakh conflict to test reconciliation)
    conflict_path = target_dir / "Conflicting_Report.pdf"
    doc_c = SimpleDocTemplate(str(conflict_path), pagesize=letter)
    story_c = [
        Paragraph("Preliminary Financial Bulletin (Unaudited Draft)", styles["Title"]),
        Spacer(1, 14),
        Paragraph(
            "In an earlier unaudited disclosure, total Q2 revenue was preliminarily estimated at ₹905 lakh "
            "prior to inventory and rebate reconciliations.",
            styles["Normal"]
        ),
    ]
    doc_c.build(story_c)
    print(f"Generated {conflict_path.name}")

if __name__ == "__main__":
    generate_samples(Path(__file__).resolve().parent.parent / "data" / "sample_documents")
