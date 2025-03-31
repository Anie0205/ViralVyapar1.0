import os
import json
import shutil
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

# ✅ Paths
SEO_DATA_FILE = "output/seo_analysis.json"
OUTPUT_PDF = "output/seo_report.pdf"
TEMP_DIR = "output/temp_charts"

# ✅ Create temporary directory for charts
os.makedirs(TEMP_DIR, exist_ok=True)

# ✅ Pastel color palette
PASTEL_COLORS = ['#FFB3BA', '#FFDFBA', '#FFFFBA', '#BAFFC9', '#BAE1FF', '#D7BDE2', '#A9CCE3', '#AED6F1', '#A3E4D7']

# ✅ Function to load SEO data
def load_seo_data():
    """Load SEO analysis data from JSON file."""
    with open(SEO_DATA_FILE, "r") as f:
        return json.load(f)

# ✅ Function to create visualizations
def create_visualizations(seo_data):
    """Generates and saves visualizations as PNG images."""
    chart_paths = []

    # 📊 1. Backlink Distribution
    if "backlinks" in seo_data:
        domains = [item["domain"] for item in seo_data["backlinks"]]
        scores = [item["page_rank_decimal"] for item in seo_data["backlinks"]]

        plt.figure(figsize=(10, 6))
        plt.barh(domains, scores, color=PASTEL_COLORS[:len(domains)])
        plt.title("Backlink Authority Distribution")
        plt.xlabel("Page Rank (Decimal)")
        plt.ylabel("Domain")
        chart_path = os.path.join(TEMP_DIR, "backlinks.png")
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        chart_paths.append(chart_path)

    # 📈 2. Keyword Performance
    if "keywords" in seo_data:
        keywords = [kw["keyword"] for kw in seo_data["keywords"]]
        ctr = [kw["ctr"] for kw in seo_data["keywords"]]
        difficulty = [kw["difficulty"] for kw in seo_data["keywords"]]

        plt.figure(figsize=(12, 6))
        plt.scatter(ctr, difficulty, c=PASTEL_COLORS[0], label="CTR vs Difficulty", alpha=0.7, edgecolors="black")
        plt.xlabel("Click-Through Rate (CTR)")
        plt.ylabel("Keyword Difficulty")
        plt.title("Keyword Performance")
        plt.grid(True)
        chart_path = os.path.join(TEMP_DIR, "keyword_performance.png")
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        chart_paths.append(chart_path)

    return chart_paths

# ✅ Function to generate PDF report
def generate_pdf(seo_data, chart_paths):
    """Generates the SEO report PDF with charts."""
    doc = SimpleDocTemplate(OUTPUT_PDF, pagesize=LETTER)
    styles = getSampleStyleSheet()
    content = []

    # ✅ Title Page
    content.append(Paragraph("SEO Analysis Report", styles["Title"]))
    content.append(Spacer(1, 12))
    content.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    content.append(Spacer(1, 24))

    # ✅ Summary Section
    content.append(Paragraph("### Summary", styles["Heading2"]))
    content.append(Spacer(1, 12))
    
    summary_data = [
        ["Total Keywords", len(seo_data.get("keywords", []))],
        ["Total Backlinks", len(seo_data.get("backlinks", []))],
        ["Competitor Domains", len(seo_data.get("competitors", []))]
    ]
    
    table = Table(summary_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(PASTEL_COLORS[1])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(PASTEL_COLORS[3])),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(table)
    content.append(Spacer(1, 24))

    # ✅ Add Visualizations
    content.append(Paragraph("### Visualizations", styles["Heading2"]))
    content.append(Spacer(1, 12))

    for chart in chart_paths:
        content.append(Image(chart, width=500, height=300))
        content.append(Spacer(1, 12))

    # ✅ Add Recommendations
    content.append(Paragraph("### Recommendations", styles["Heading2"]))
    content.append(Spacer(1, 12))
    content.append(Paragraph(
        "- **Improve Backlink Quality:** Focus on obtaining backlinks from high-authority domains.\n"
        "- **Optimize Keywords:** Prioritize keywords with high CTR and moderate difficulty.\n"
        "- **Competitor Analysis:** Monitor competitors' backlink strategies and keyword performance.",
        styles["Normal"]
    ))

    # ✅ Build the PDF
    doc.build(content)
    print(f"✅ SEO report saved to: {OUTPUT_PDF}")

# ✅ Cleanup temporary image files
def cleanup_temp_images():
    """Removes the temporary chart image files."""
    shutil.rmtree(TEMP_DIR)

# ✅ Main Execution
def main():
    print("🔍 Generating SEO report with visualizations...")
    
    # ✅ Load SEO data
    seo_data = load_seo_data()

    # ✅ Generate visualizations
    chart_paths = create_visualizations(seo_data)

    # ✅ Generate PDF report
    generate_pdf(seo_data, chart_paths)

    # ✅ Cleanup
    cleanup_temp_images()

if __name__ == "__main__":
    main()
