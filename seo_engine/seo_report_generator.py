import os
import json
import shutil
import matplotlib.pyplot as plt
import seaborn as sns
from reportlab.lib.pagesizes import LETTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
from typing import Dict, List

# ✅ Paths
TEMP_DIR = "output/temp_charts"
os.makedirs(TEMP_DIR, exist_ok=True)

# ✅ Color palette
COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD', '#D4A5A5', '#9B59B6', '#3498DB', '#E67E22']

def create_visualizations(
    seo_analysis: Dict,
    keyword_data: Dict,
    competitor_data: List[str],
    backlink_data: Dict,
    intent_data: Dict
) -> List[str]:
    """Generates and saves visualizations as PNG images."""
    chart_paths = []

    # 1. Overall SEO Score Distribution
    plt.figure(figsize=(10, 6))
    scores = [data['overall_score'] for data in seo_analysis.values()]
    plt.hist(scores, bins=10, color=COLORS[0], alpha=0.7)
    plt.title("Distribution of Overall SEO Scores")
    plt.xlabel("Score")
    plt.ylabel("Frequency")
    chart_path = os.path.join(TEMP_DIR, "score_distribution.png")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    chart_paths.append(chart_path)

    # 2. Component Score Comparison
    plt.figure(figsize=(12, 6))
    components = ['content_quality', 'technical_seo', 'keyword_optimization', 'backlink_profile', 'user_experience']
    avg_scores = []
    for comp in components:
        scores = [data['component_scores'][comp] for data in seo_analysis.values()]
        avg_scores.append(sum(scores) / len(scores))
    
    plt.bar(components, avg_scores, color=COLORS[1:6])
    plt.title("Average Component Scores")
    plt.xticks(rotation=45)
    plt.ylabel("Score")
    chart_path = os.path.join(TEMP_DIR, "component_scores.png")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    chart_paths.append(chart_path)

    # 3. Keyword Distribution
    plt.figure(figsize=(12, 6))
    keyword_freq = keyword_data.get('keyword_frequencies', {})
    top_keywords = dict(sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10])
    plt.bar(top_keywords.keys(), top_keywords.values(), color=COLORS[2])
    plt.title("Top 10 Keywords")
    plt.xticks(rotation=45)
    plt.ylabel("Frequency")
    chart_path = os.path.join(TEMP_DIR, "keyword_distribution.png")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    chart_paths.append(chart_path)

    # 4. Search Intent Distribution
    plt.figure(figsize=(10, 6))
    intents = defaultdict(int)
    for query_data in intent_data.values():
        intents[query_data['primary_intent']] += 1
    
    plt.pie(intents.values(), labels=intents.keys(), colors=COLORS[3:6], autopct='%1.1f%%')
    plt.title("Search Intent Distribution")
    chart_path = os.path.join(TEMP_DIR, "search_intent.png")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    chart_paths.append(chart_path)

    # 5. Backlink Authority Distribution
    plt.figure(figsize=(10, 6))
    domains = list(backlink_data.keys())
    scores = [len(backlinks) for backlinks in backlink_data.values()]
    plt.barh(domains, scores, color=COLORS[6])
    plt.title("Backlink Authority Distribution")
    plt.xlabel("Number of Backlinks")
    plt.ylabel("Domain")
    chart_path = os.path.join(TEMP_DIR, "backlink_distribution.png")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close()
    chart_paths.append(chart_path)

    return chart_paths

def generate_report(
    seo_analysis: Dict,
    keyword_data: Dict,
    competitor_data: List[str],
    backlink_data: Dict,
    intent_data: Dict,
    rag_content: str
):
    """Generates the comprehensive SEO report PDF."""
    doc = SimpleDocTemplate("output/seo_report.pdf", pagesize=LETTER)
    styles = getSampleStyleSheet()
    content = []

    # Title Page
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30
    )
    content.append(Paragraph("Comprehensive SEO Analysis Report", title_style))
    content.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    content.append(PageBreak())

    # Executive Summary
    content.append(Paragraph("Executive Summary", styles['Heading1']))
    content.append(Spacer(1, 12))
    
    # Calculate average score safely
    avg_score_str = "N/A"
    if seo_analysis and isinstance(seo_analysis, dict) and len(seo_analysis) > 0:
        try:
            valid_scores = [data['overall_score'] for data in seo_analysis.values() if isinstance(data, dict) and 'overall_score' in data]
            if valid_scores:
                avg_score = sum(valid_scores) / len(valid_scores)
                avg_score_str = f"{avg_score:.2f}"
        except Exception as e:
            print(f"⚠️ Error calculating average SEO score: {e}")
            avg_score_str = "Error"
    else:
        print("⚠️ SEO analysis data is empty or invalid for calculating average score.")

    summary_data = [
        ["Total Competitors", len(competitor_data) if competitor_data else 0],
        ["Total Keywords", len(keyword_data.get('keyword_frequencies', {})) if keyword_data else 0],
        ["Total Backlinks", sum(len(backlinks) for backlinks in backlink_data.values()) if backlink_data else 0],
        ["Average SEO Score", avg_score_str] # Use calculated or default string
    ]
    
    table = Table(summary_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS[0])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor(COLORS[1])),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(table)
    content.append(PageBreak())

    # Visualizations
    content.append(Paragraph("Key Metrics Visualizations", styles['Heading1']))
    content.append(Spacer(1, 12))
    
    chart_paths = create_visualizations(
        seo_analysis,
        keyword_data,
        competitor_data,
        backlink_data,
        intent_data
    )
    
    for chart in chart_paths:
        content.append(Image(chart, width=500, height=300))
        content.append(Spacer(1, 12))
    content.append(PageBreak())

    # Detailed Analysis
    content.append(Paragraph("Detailed Analysis", styles['Heading1']))
    content.append(Spacer(1, 12))

    # Top Competitors
    content.append(Paragraph("Top Performing Competitors", styles['Heading2']))
    content.append(Spacer(1, 12))
    
    top_competitors = sorted(
        seo_analysis.items(),
        key=lambda x: x[1]['overall_score'],
        reverse=True
    )[:5]
    
    competitor_data = [["Domain", "Overall Score", "Content Quality", "Technical SEO"]]
    for domain, data in top_competitors:
        competitor_data.append([
            domain,
            f"{data['overall_score']:.2f}",
            f"{data['component_scores']['content_quality']:.2f}",
            f"{data['component_scores']['technical_seo']:.2f}"
        ])
    
    table = Table(competitor_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLORS[2])),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    content.append(table)
    content.append(PageBreak())

    # Recommendations
    content.append(Paragraph("Key Recommendations", styles['Heading1']))
    content.append(Spacer(1, 12))
    
    recommendations = []
    for domain, data in seo_analysis.items():
        if data['overall_score'] < 0.7:
            recommendations.extend(data['recommendations'])
    
    for rec in set(recommendations):  # Remove duplicates
        content.append(Paragraph(f"• {rec}", styles['Normal']))
    content.append(PageBreak())

    # AI-Generated Content
    content.append(Paragraph("AI-Generated Content Suggestions", styles['Heading1']))
    content.append(Spacer(1, 12))
    content.append(Paragraph(rag_content, styles['Normal']))

    # Build PDF
    doc.build(content)
    print(f"✅ Comprehensive SEO report saved to: output/seo_report.pdf")

    # Cleanup
    shutil.rmtree(TEMP_DIR)

if __name__ == "__main__":
    # Load all required data
    with open('output/seo_analysis.json', 'r') as f:
        seo_analysis = json.load(f)
    with open('output/extracted_keywords.json', 'r') as f:
        keyword_data = json.load(f)
    with open('output/competitor_domains.json', 'r') as f:
        competitor_data = json.load(f)
    with open('output/high_authority_backlinks.json', 'r') as f:
        backlink_data = json.load(f)
    with open('output/search_intents.json', 'r') as f:
        intent_data = json.load(f)
    with open('output/refined_content.json', 'r') as f:
        rag_content = json.load(f)

    # Generate report
    generate_report(
        seo_analysis=seo_analysis,
        keyword_data=keyword_data,
        competitor_data=competitor_data,
        backlink_data=backlink_data,
        intent_data=intent_data,
        rag_content=rag_content
    )
