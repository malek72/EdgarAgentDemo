"""Simple direct PDF test to verify PDF generation works"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
from datetime import datetime

print("="*80)
print("DIRECT PDF GENERATION TEST")
print("="*80 + "\n")

# Output path
output_dir = Path("agent3_reports")
pdf_path = output_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

# Create PDF
doc = SimpleDocTemplate(
    str(pdf_path),
    pagesize=letter,
    rightMargin=0.75*inch,
    leftMargin=0.75*inch,
    topMargin=1*inch,
    bottomMargin=0.75*inch
)

styles = getSampleStyleSheet()
story = []

# Title
title_style = ParagraphStyle(
    'Title',
    parent=styles['Heading1'],
    fontSize=24,
    textColor=colors.HexColor('#1a1a1a'),
    spaceAfter=30,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

story.append(Paragraph("Investment Analysis Report", title_style))
story.append(Paragraph("<i>Test Report with Financial Figures</i>", styles['Normal']))
story.append(Paragraph(f"<i>Generated: {datetime.now().strftime('%B %d, %Y')}</i>", styles['Normal']))
story.append(Spacer(1, 0.5*inch))

# Executive Summary
story.append(Paragraph("<b>1. EXECUTIVE SUMMARY</b>", styles['Heading1']))
story.append(Spacer(1, 0.1*inch))

story.append(Paragraph("<b>Investment Recommendation:</b> Buy", styles['BodyText']))
story.append(Paragraph("<b>Target Valuation:</b> $350M - $550M", styles['BodyText']))
story.append(Paragraph("<b>Expected IRR:</b> 22-31% over 3-5 years", styles['BodyText']))
story.append(Spacer(1, 0.2*inch))

# Financial Table
story.append(Paragraph("<b>Key Financial Metrics</b>", styles['Heading2']))
story.append(Spacer(1, 0.1*inch))

table_data = [
    ['Metric', '2023', '2024', '2025E', 'Growth'],
    ['Revenue ($M)', '843', '1,100', '1,450', '32%'],
    ['Gross Margin', '65%', '66%', '67%', '+2pp'],
    ['EBITDA Margin', '25%', '27%', '30%', '+5pp'],
    ['Market Share', '12%', '14%', '16%', '+4pp']
]

t = Table(table_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 10),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('FONTSIZE', (0, 1), (-1, -1), 9),
]))

story.append(t)
story.append(Spacer(1, 0.3*inch))

# Page break before charts
story.append(PageBreak())
story.append(Paragraph("<b>Financial Figures & Visualizations</b>", styles['Heading1']))
story.append(Spacer(1, 0.2*inch))

# Chart 1: Market Size Growth
fig, ax = plt.subplots(figsize=(8, 5))
years = [2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2032, 2034]
market_sizes = [843, 1100, 1450, 1900, 2500, 3200, 4000, 5000, 6200, 10000]

ax.plot(years, market_sizes, marker='o', linewidth=2.5, markersize=10, color='#3498db', label='Market Size')
ax.fill_between(years, market_sizes, alpha=0.3, color='#3498db')
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Market Size ($M)', fontsize=12, fontweight='bold')
ax.set_title('Market Size Growth Projection (2023-2034)', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)
ax.legend(fontsize=10)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}M'))
plt.tight_layout()

img_buffer1 = io.BytesIO()
plt.savefig(img_buffer1, format='png', dpi=150, bbox_inches='tight')
img_buffer1.seek(0)
plt.close()

story.append(Image(img_buffer1, width=6*inch, height=3.75*inch))
story.append(Spacer(1, 0.3*inch))

# Chart 2: Competitive Market Share
fig, ax = plt.subplots(figsize=(8, 5))
companies = ['Xpansiv', 'Verra', 'Gold Standard', 'Climate Impact X', 'AirCarbon', 'Others']
market_shares = [16.7, 14.2, 11.3, 8.8, 7.2, 41.8]
colors_list = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#95a5a6']

bars = ax.bar(companies, market_shares, color=colors_list, edgecolor='black', linewidth=1.5)
ax.set_ylabel('Market Share (%)', fontsize=12, fontweight='bold')
ax.set_title('Competitive Market Share Analysis', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, axis='y', alpha=0.3)
ax.set_ylim(0, 50)

for i, (bar, value) in enumerate(zip(bars, market_shares)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
            f'{value}%', ha='center', va='bottom', fontweight='bold', fontsize=10)

plt.xticks(rotation=45, ha='right')
plt.tight_layout()

img_buffer2 = io.BytesIO()
plt.savefig(img_buffer2, format='png', dpi=150, bbox_inches='tight')
img_buffer2.seek(0)
plt.close()

story.append(Image(img_buffer2, width=6*inch, height=3.75*inch))
story.append(Spacer(1, 0.3*inch))

# Chart 3: Revenue & Margin Trends
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

# Revenue growth
quarters = ['Q1\n2024', 'Q2\n2024', 'Q3\n2024', 'Q4\n2024', 'Q1\n2025', 'Q2\n2025']
revenue = [8.5, 10.2, 11.8, 13.5, 15.8, 18.2]

ax1.plot(quarters, revenue, marker='o', linewidth=2.5, markersize=8, color='#2ecc71')
ax1.fill_between(range(len(quarters)), revenue, alpha=0.2, color='#2ecc71')
ax1.set_ylabel('Revenue ($M)', fontsize=10, fontweight='bold')
ax1.set_title('Quarterly Revenue Growth', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.1f}M'))

# Margin trends
margins = [62, 64, 65, 66, 66, 67]
ax2.plot(quarters, margins, marker='s', linewidth=2.5, markersize=8, color='#e74c3c')
ax2.fill_between(range(len(quarters)), margins, alpha=0.2, color='#e74c3c')
ax2.set_ylabel('Gross Margin (%)', fontsize=10, fontweight='bold')
ax2.set_title('Gross Margin Trend', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.set_ylim(60, 70)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f}%'))

plt.tight_layout()

img_buffer3 = io.BytesIO()
plt.savefig(img_buffer3, format='png', dpi=150, bbox_inches='tight')
img_buffer3.seek(0)
plt.close()

story.append(Image(img_buffer3, width=7*inch, height=2.8*inch))
story.append(Spacer(1, 0.3*inch))

# Chart 4: Valuation Comparison
fig, ax = plt.subplots(figsize=(8, 5))

companies_val = ['Xpansiv', 'Verra', 'Climate\nImpact X', 'Target\nPlatform']
ev_revenue = [12.5, 8.2, 15.3, 14.0]
colors_val = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']

bars = ax.bar(companies_val, ev_revenue, color=colors_val, edgecolor='black', linewidth=1.5)
ax.set_ylabel('EV / Revenue Multiple', fontsize=12, fontweight='bold')
ax.set_title('Valuation Comparison (EV/Revenue)', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, axis='y', alpha=0.3)
ax.set_ylim(0, 18)

for bar, value in zip(bars, ev_revenue):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.2,
            f'{value}x', ha='center', va='bottom', fontweight='bold', fontsize=10)

plt.tight_layout()

img_buffer4 = io.BytesIO()
plt.savefig(img_buffer4, format='png', dpi=150, bbox_inches='tight')
img_buffer4.seek(0)
plt.close()

story.append(Image(img_buffer4, width=6*inch, height=3.75*inch))

# Build PDF
print("Building PDF with 4 financial charts...\n")
doc.build(story)

print(f"✅ PDF GENERATED SUCCESSFULLY!\n")
print(f"Location: {pdf_path}")
print(f"Size: {pdf_path.stat().st_size:,} bytes ({pdf_path.stat().st_size/1024:.1f} KB)")
print(f"\nCharts included:")
print(f"  1. Market Size Growth Projection (2023-2034)")
print(f"  2. Competitive Market Share Analysis")
print(f"  3. Quarterly Revenue & Margin Trends")
print(f"  4. Valuation Comparison (EV/Revenue)")
print("\n" + "="*80)

EOF

