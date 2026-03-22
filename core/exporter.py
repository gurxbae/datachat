from fpdf import FPDF
import os
from datetime import date

def clean_text(text):
    """Remove characters fpdf cannot handle."""
    replacements = {
        "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u2022": "*", "\u25cf": "*",
        "\u20b9": "Rs.", "\u00a0": " ", "\u2026": "...", "\u00ae": "(R)",
        "\u2122": "(TM)", "\u00a9": "(C)"
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text.encode("latin-1", errors="ignore").decode("latin-1")

def export_session_pdf(history, filename="datachat_report.pdf"):
    """Exports full session history as a PDF report."""

    pdf = FPDF()
    pdf.set_margins(20, 20, 20)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "DataChat - Session Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Generated: {date.today().strftime('%B %d, %Y')}",
             ln=True, align="C")
    pdf.ln(4)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(8)

    if not history:
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, "No queries in this session.", ln=True)
    else:
        for i, item in enumerate(history):
            # Question
            pdf.set_font("Helvetica", "B", 12)
            q = clean_text(f"Q{i+1}: {item['question']}")
            pdf.multi_cell(0, 7, q)
            pdf.ln(2)

            # SQL
            pdf.set_font("Helvetica", "I", 9)
            sql = clean_text(f"SQL: {item['sql']}")
            pdf.multi_cell(0, 6, sql)
            pdf.ln(2)

            # Results table
            if item["df"] is not None and not item["df"].empty:
                pdf.set_font("Helvetica", "B", 9)
                df = item["df"].head(10)

                # Headers
                col_width = 170 / len(df.columns)
                for col in df.columns:
                    pdf.cell(col_width, 6,
                             clean_text(str(col))[:20],
                             border=1)
                pdf.ln()

                # Rows
                pdf.set_font("Helvetica", "", 9)
                for _, row in df.iterrows():
                    for val in row:
                        pdf.cell(col_width, 6,
                                 clean_text(str(val))[:20],
                                 border=1)
                    pdf.ln()

            pdf.ln(6)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(6)

    os.makedirs("exports", exist_ok=True)
    output_path = f"exports/{filename}"
    pdf.output(output_path)
    return output_path