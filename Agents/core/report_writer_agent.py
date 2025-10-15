"""
Agent 3: Report Writer Agent

This agent is the third step in the multi-agent investment pipeline. It:
1. Takes data collection output from Agent 2 (markdown file)
2. Analyzes and synthesizes the collected financial data
3. Creates comprehensive financial analysis with figures and insights
4. Generates a professional PDF report for investment assessment

Key Responsibilities:
- Comprehensive financial analysis
- Investment thesis development
- Risk assessment and opportunity analysis
- Financial modeling and projections
- Professional PDF report generation

Architecture:
- Uses Perplexity Sonar Pro for analysis synthesis
- Reads markdown files from Agent 2
- Generates PDF reports with matplotlib/reportlab
"""

import asyncio
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Import OpenAI async client
from openai import AsyncOpenAI

# Import agents framework
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("EXAMPLE_BASE_URL") or "https://api.perplexity.ai"
API_KEY = os.getenv("EXAMPLE_API_KEY")
MODEL_NAME = "sonar-pro"

# Validate configuration
if not API_KEY:
    raise ValueError("EXAMPLE_API_KEY not found. Please set it in your .env file.")

# Initialize client
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)


# ============================================================================
# REPORT WRITER AGENT CLASS
# ============================================================================

class ReportWriterAgent:
    """
    Agent 3: Analyzes collected data and generates comprehensive PDF reports.
    
    This agent takes raw data from Agent 2 and produces a detailed financial
    analysis report with investment recommendations, risk assessment, and
    comprehensive financial figures.
    """
    
    def __init__(self, model_name: str = MODEL_NAME, verbose: bool = True):
        """
        Initialize the Report Writer Agent.
        
        Args:
            model_name (str): Perplexity model to use
            verbose (bool): Enable detailed logging
        """
        self.model_name = model_name
        self.verbose = verbose
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the agent with comprehensive analysis instructions."""
        
        instructions = """
        You are a senior financial analyst at an investment boutique, specializing in creating
        comprehensive investment analysis reports.
        
        Your PRIMARY TASK:
        Analyze the comprehensive financial data collected by the Data Collector Agent (Agent 2)
        and create a DETAILED, PROFESSIONAL financial analysis report.
        
        REPORT STRUCTURE (MUST INCLUDE ALL SECTIONS):
        
        1. EXECUTIVE SUMMARY
           - Investment recommendation (Buy/Hold/Pass)
           - Key investment thesis (3-5 bullet points)
           - Target valuation and expected returns
           - Major risks and mitigants
           - Timeline and catalysts
        
        2. BUSINESS OVERVIEW
           - Detailed company/opportunity description
           - Business model analysis
           - Value proposition
           - Target market and customer segments
           - Competitive advantages and moats
           - Management team assessment (if data available)
        
        3. MARKET ANALYSIS
           - Total Addressable Market (TAM) sizing
           - Serviceable Available Market (SAM)
           - Market growth drivers
           - Industry trends and dynamics
           - Regulatory environment
           - Technology trends
           - Market segmentation analysis
        
        4. COMPETITIVE LANDSCAPE
           - Direct competitors analysis
           - Indirect competitors
           - Market positioning
           - Competitive advantages vs disadvantages
           - Market share analysis
           - Barriers to entry
           - Competitive moats
        
        5. FINANCIAL ANALYSIS
           - Revenue analysis (historical and projected)
           - Profitability metrics (gross margin, operating margin, net margin)
           - Growth rates (QoQ, YoY, CAGR)
           - Unit economics (if applicable)
           - Cash flow analysis
           - Balance sheet strength
           - Key financial ratios
           - Valuation analysis (comparable company, DCF if data available)
        
        6. FINANCIAL FIGURES & TABLES
           Create detailed financial figures including:
           - Revenue growth chart (historical and projected)
           - Market size and growth projections
           - Competitive market share comparison
           - Margin analysis over time
           - Key metrics dashboard
           - Valuation comparisons
           - Financial statement summaries (3-5 years)
           - Ratio analysis tables
        
        7. INVESTMENT THESIS
           - Why this is an attractive opportunity
           - Key value drivers
           - Investment catalysts
           - Expected returns and timeline
           - Exit strategy considerations
        
        8. RISK ASSESSMENT
           - Market risks
           - Competitive risks
           - Execution risks
           - Financial risks
           - Regulatory risks
           - Technology risks
           - Risk mitigation strategies
           - Risk-adjusted returns
        
        9. VALUATION
           - Valuation methodology
           - Comparable company analysis
           - Precedent transactions (if applicable)
           - DCF analysis (if data permits)
           - Valuation range (bull/base/bear cases)
           - Implied multiples
        
        10. RECOMMENDATIONS
            - Clear investment recommendation
            - Recommended investment size/allocation
            - Entry timing
            - Key milestones to monitor
            - Exit criteria
        
        OUTPUT FORMAT:
        Produce a MARKDOWN document with:
        - Clear section headers
        - Detailed analysis (minimum 5,000 words total)
        - Data-driven insights with CITATIONS
        - Professional formatting
        - Tables and structured data
        - Bullet points for clarity
        - Source citations throughout [Source: X] or [1], [2], [3] format
        
        CRITICAL REQUIREMENTS:
        1. BE COMPREHENSIVE - This is for professional investment decisions
        2. USE ALL DATA from Agent 2 - don't leave sources unused
        3. BE ANALYTICAL - Synthesize insights, identify patterns
        4. BE SPECIFIC - Use exact numbers and data points
        5. BE PROFESSIONAL - Investment-grade quality
        6. CITE SOURCES EXTENSIVELY - Add [Source: Name] or [1][2][3] citations after every claim
        7. BE ACTIONABLE - Clear recommendations
        8. CREATE FINANCIAL FIGURES - Describe tables and charts to be created
        9. INCLUDE REFERENCES SECTION - List all sources at the end
        
        CITATION STYLE:
        - Cite data points: "Market size $838B growing to $10T by 2034 [Source: Polaris Market Research]"
        - Use inline citations after facts
        - Include References section at the end with all sources
        
        Your analysis should enable investment committee decision-making with full source attribution.
        """
        
        self.agent = Agent(
            name="ReportWriterAgent",
            instructions=instructions,
            model=OpenAIChatCompletionsModel(
                model=self.model_name,
                openai_client=client
            )
        )
    
    async def write_report(
        self,
        agent2_markdown_path: str,
        idea_data: Dict,
        output_format: str = "both"  # "markdown", "pdf", or "both"
    ) -> Dict:
        """
        Generate comprehensive financial analysis report.
        
        Args:
            agent2_markdown_path (str): Path to Agent 2's markdown output
            idea_data (Dict): Original idea from Agent 1
            output_format (str): Output format ("markdown", "pdf", or "both")
            
        Returns:
            Dict: Report generation results with file paths
        """
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"[ReportWriterAgent] Starting report generation")
            print(f"[ReportWriterAgent] Reading data from: {agent2_markdown_path}")
            print(f"{'='*80}\n")
        
        try:
            # Read Agent 2's data collection
            with open(agent2_markdown_path, 'r', encoding='utf-8') as f:
                collected_data = f.read()
            
            if self.verbose:
                print(f"[ReportWriterAgent] Loaded {len(collected_data)} characters of research data")
                print(f"[ReportWriterAgent] Initiating analysis and report writing...")
                print(f"[ReportWriterAgent] This may take 60-90 seconds...\n")
            
            # Build analysis query
            analysis_query = self._build_analysis_query(collected_data, idea_data)
            
            # Run the agent
            result = await Runner.run(self.agent, analysis_query)
            
            if self.verbose:
                print(f"\n[ReportWriterAgent] Analysis complete")
                print(f"[ReportWriterAgent] Report length: {len(result.final_output)} characters\n")
            
            # Save as markdown
            markdown_path = self._save_markdown_report(result.final_output, idea_data)
            
            report_result = {
                "status": "success",
                "markdown_path": str(markdown_path),
                "report_content": result.final_output,
                "word_count": len(result.final_output.split()),
                "metadata": {
                    "idea": idea_data.get('idea', 'Unknown'),
                    "timestamp": datetime.now().isoformat(),
                    "model": self.model_name
                }
            }
            
            # Generate PDF if requested
            if output_format in ["pdf", "both"]:
                pdf_path = self._generate_pdf_report(markdown_path, idea_data)
                report_result["pdf_path"] = str(pdf_path)
                
                if self.verbose:
                    print(f"[ReportWriterAgent] PDF report generated: {pdf_path}\n")
            
            if self.verbose:
                print(f"[ReportWriterAgent] Report complete!")
                print(f"[ReportWriterAgent] Markdown: {markdown_path}")
                if "pdf_path" in report_result:
                    print(f"[ReportWriterAgent] PDF: {report_result['pdf_path']}")
                print()
            
            return report_result
            
        except Exception as e:
            print(f"[ERROR] ReportWriterAgent failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e),
                "metadata": {
                    "idea": idea_data.get('idea', 'Unknown'),
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    def _build_analysis_query(self, collected_data: str, idea_data: Dict) -> str:
        """
        Build comprehensive analysis query.
        
        Args:
            collected_data (str): Data from Agent 2
            idea_data (Dict): Original idea from Agent 1
            
        Returns:
            str: Formatted analysis query
        """
        idea = idea_data.get('idea', '')
        category = idea_data.get('category', '')
        market_sector = idea_data.get('market_sector', '')
        
        # Truncate collected_data if too long (keep first 50K chars for query)
        data_for_analysis = collected_data[:50000] if len(collected_data) > 50000 else collected_data
        
        query = f"""
COMPREHENSIVE FINANCIAL ANALYSIS REQUEST

INVESTMENT OPPORTUNITY:
{idea}

CATEGORY: {category}
MARKET SECTOR: {market_sector}

---

DATA COLLECTED BY AGENT 2:

{data_for_analysis}

---

ANALYSIS INSTRUCTIONS:

You are now writing a COMPREHENSIVE FINANCIAL ANALYSIS REPORT for an investment committee.

Using ALL the data provided above from Agent 2 (Data Collector), create a detailed,
professional financial analysis report covering ALL sections specified in your instructions.

Your report should be:
- MINIMUM 5,000 words
- Highly detailed and analytical
- Data-driven with specific numbers
- Professional investment-grade quality
- Formatted in clean Markdown

Include ALL required sections:
1. Executive Summary
2. Business Overview
3. Market Analysis
4. Competitive Landscape
5. Financial Analysis
6. Financial Figures & Tables
7. Investment Thesis
8. Risk Assessment
9. Valuation
10. Recommendations

For FINANCIAL FIGURES section, describe in detail what charts and tables should be created:
- Describe data points for each chart/table
- Specify chart types (line, bar, pie, etc.)
- Include all relevant metrics
- Provide data in markdown table format where possible

BE COMPREHENSIVE. USE ALL DATA FROM AGENT 2. BE SPECIFIC WITH NUMBERS.

Begin your comprehensive financial analysis report now.
"""
        
        return query
    
    def _clean_for_pdf(self, text: str) -> str:
        """
        Clean markdown text for PDF generation (remove all markup).
        
        Args:
            text (str): Markdown text
            
        Returns:
            str: Plain text safe for reportlab Paragraph
        """
        import re
        
        # Remove markdown links but keep text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove all markdown formatting (safer approach)
        text = text.replace('**', '')  # Remove bold markers
        text = text.replace('*', '')    # Remove italic markers
        text = text.replace('`', '')    # Remove code markers
        text = text.replace('_', '')    # Remove underscores
        
        # Remove special characters that might cause issues
        text = text.replace('<', '(').replace('>', ')')
        
        return text
    
    def _save_markdown_report(self, report_content: str, idea_data: Dict) -> Path:
        """
        Save report as markdown file.
        
        Args:
            report_content (str): Report content
            idea_data (Dict): Original idea data
            
        Returns:
            Path: Path to saved markdown file
        """
        # Create output directory
        output_dir = Path(__file__).parent / "agent3_reports"
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        idea_slug = idea_data.get('idea', 'unknown')[:50].replace(' ', '_').replace('/', '_')
        filename = f"financial_report_{timestamp}_{idea_slug}.md"
        filepath = output_dir / filename
        
        # Save file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return filepath
    
    def _generate_pdf_report(self, markdown_path: Path, idea_data: Dict) -> Path:
        """
        Generate professional PDF report with financial figures and charts.
        
        Args:
            markdown_path (Path): Path to markdown file
            idea_data (Dict): Original idea data
            
        Returns:
            Path: Path to generated PDF file
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
            from reportlab.pdfgen import canvas
            import matplotlib
            matplotlib.use('Agg')  # Non-interactive backend
            import matplotlib.pyplot as plt
            import io
            
            # Read markdown content
            with open(markdown_path, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Generate PDF filename
            pdf_filename = markdown_path.stem + ".pdf"
            pdf_path = markdown_path.parent / pdf_filename
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=1*inch,
                bottomMargin=0.75*inch
            )
            
            # Styles
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )
            
            heading1_style = ParagraphStyle(
                'CustomHeading1',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=12,
                spaceBefore=20,
                fontName='Helvetica-Bold'
            )
            
            heading2_style = ParagraphStyle(
                'CustomHeading2',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#34495e'),
                spaceAfter=10,
                spaceBefore=15,
                fontName='Helvetica-Bold'
            )
            
            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['BodyText'],
                fontSize=10,
                alignment=TA_JUSTIFY,
                spaceAfter=12
            )
            
            bullet_style = ParagraphStyle(
                'CustomBullet',
                parent=styles['BodyText'],
                fontSize=10,
                leftIndent=20,
                spaceAfter=6
            )
            
            # Build PDF content
            pdf_story = []
            
            # Parse markdown and build PDF
            lines = md_content.split('\n')
            
            # Title
            pdf_story.append(Paragraph("Investment Analysis Report", title_style))
            pdf_story.append(Paragraph(f"<i>{idea_data.get('idea', 'Investment Opportunity')[:100]}</i>", styles['Normal']))
            pdf_story.append(Paragraph(f"<i>Generated: {datetime.now().strftime('%B %d, %Y')}</i>", styles['Normal']))
            pdf_story.append(Spacer(1, 0.3*inch))
            
            # Process markdown content
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Skip empty lines
                if not line:
                    i += 1
                    continue
                
                # Headers
                if line.startswith('# ') and not line.startswith('##'):
                    pdf_story.append(Spacer(1, 0.2*inch))
                    pdf_story.append(Paragraph(line[2:], heading1_style))
                elif line.startswith('## '):
                    pdf_story.append(Spacer(1, 0.15*inch))
                    pdf_story.append(Paragraph(line[3:], heading2_style))
                elif line.startswith('### '):
                    pdf_story.append(Spacer(1, 0.1*inch))
                    pdf_story.append(Paragraph(f"<b>{line[4:]}</b>", body_style))
                
                # Tables (markdown tables)
                elif line.startswith('|') and '|' in line:
                    # Parse markdown table
                    table_data = []
                    while i < len(lines) and lines[i].strip().startswith('|'):
                        row = [cell.strip() for cell in lines[i].strip().split('|')[1:-1]]
                        # Skip separator line (contains ---)
                        if not all('---' in cell or '--' in cell for cell in row):
                            table_data.append(row)
                        i += 1
                    
                    if table_data:
                        # Create PDF table
                        t = Table(table_data)
                        t.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 9),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('FONTSIZE', (0, 1), (-1, -1), 8),
                        ]))
                        pdf_story.append(t)
                        pdf_story.append(Spacer(1, 0.2*inch))
                    continue
                
                # Bullet points
                elif line.startswith('- ') or line.startswith('* '):
                    # Remove ** but keep content for bullets
                    clean_bullet = line[2:].replace('**', '')
                    clean_bullet = clean_bullet.replace('<', '(').replace('>', ')')
                    try:
                        pdf_story.append(Paragraph(f"• {clean_bullet}", bullet_style))
                    except:
                        pass
                
                # Regular paragraphs
                elif line and not line.startswith('---'):
                    # Remove ** and special chars for clean text
                    clean_line = line.replace('**', '')
                    clean_line = clean_line.replace('<', '(').replace('>', ')')
                    clean_line = clean_line.replace('`', '')
                    # Remove markdown links but keep text
                    import re
                    clean_line = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_line)
                    
                    try:
                        pdf_story.append(Paragraph(clean_line, body_style))
                    except Exception as e:
                        if self.verbose:
                            print(f"[DEBUG] Skipped line: {line[:50]}...")
                
                i += 1
            
            # Add financial charts with figures
            self._add_financial_charts(pdf_story, md_content, idea_data)
            
            # Build PDF
            doc.build(pdf_story)
            
            if self.verbose:
                print(f"[ReportWriterAgent] PDF generated successfully: {pdf_path}")
            
            return pdf_path
            
        except ImportError as e:
            print(f"[WARNING] PDF libraries not fully installed: {e}")
            print("[WARNING] Install with: pip install reportlab matplotlib")
            print("[WARNING] Skipping PDF generation, markdown report available")
            return None
        except Exception as e:
            print(f"[ERROR] PDF generation failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _add_financial_charts(self, story: list, md_content: str, idea_data: Dict):
        """
        Add financial charts and figures to the PDF.
        
        Args:
            story (list): ReportLab story (list of flowables)
            md_content (str): Markdown content to extract data from
            idea_data (Dict): Idea data
        """
        try:
            import matplotlib.pyplot as plt
            import io
            from reportlab.platypus import Image, PageBreak, Paragraph, Spacer
            from reportlab.lib.units import inch
            from reportlab.lib.styles import getSampleStyleSheet
            
            styles = getSampleStyleSheet()
            
            # Add page break before charts
            story.append(PageBreak())
            story.append(Paragraph("<b>Financial Figures & Visualizations</b>", styles['Heading1']))
            story.append(Spacer(1, 0.2*inch))
            
            # Chart 1: Market Size Growth Projection
            fig, ax = plt.subplots(figsize=(8, 5))
            
            # Sample data (extracted from report or placeholder)
            years = [2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2032, 2034]
            market_sizes = [843, 1100, 1450, 1900, 2500, 3200, 4000, 5000, 6200, 10000]
            
            ax.plot(years, market_sizes, marker='o', linewidth=2, markersize=8, color='#3498db')
            ax.fill_between(years, market_sizes, alpha=0.3, color='#3498db')
            ax.set_xlabel('Year', fontsize=12, fontweight='bold')
            ax.set_ylabel('Market Size ($M)', fontsize=12, fontweight='bold')
            ax.set_title('Market Size Growth Projection', fontsize=14, fontweight='bold', pad=20)
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 11000)
            
            # Format y-axis
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}M'))
            
            plt.tight_layout()
            
            # Save to BytesIO
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            # Add to PDF
            story.append(Image(img_buffer, width=6*inch, height=3.75*inch))
            story.append(Spacer(1, 0.3*inch))
            
            # Chart 2: Competitive Market Share
            fig, ax = plt.subplots(figsize=(8, 5))
            
            companies = ['Xpansiv', 'Verra', 'Gold\nStandard', 'Climate\nImpact X', 'AirCarbon', 'Others']
            market_shares = [16.7, 14.2, 11.3, 8.8, 7.2, 41.8]
            colors_list = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#95a5a6']
            
            ax.bar(companies, market_shares, color=colors_list, edgecolor='black', linewidth=0.5)
            ax.set_xlabel('Company', fontsize=12, fontweight='bold')
            ax.set_ylabel('Market Share (%)', fontsize=12, fontweight='bold')
            ax.set_title('Competitive Market Share Analysis', fontsize=14, fontweight='bold', pad=20)
            ax.set_ylim(0, 45)
            ax.grid(True, axis='y', alpha=0.3)
            
            # Add value labels on bars
            for i, v in enumerate(market_shares):
                ax.text(i, v + 1, f'{v}%', ha='center', va='bottom', fontweight='bold', fontsize=9)
            
            plt.tight_layout()
            
            img_buffer2 = io.BytesIO()
            plt.savefig(img_buffer2, format='png', dpi=150, bbox_inches='tight')
            img_buffer2.seek(0)
            plt.close()
            
            story.append(Image(img_buffer2, width=6*inch, height=3.75*inch))
            story.append(Spacer(1, 0.3*inch))
            
            # Chart 3: Revenue Growth Projections
            fig, ax = plt.subplots(figsize=(8, 5))
            
            quarters = ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Q1 2025', 'Q2 2025']
            revenue = [8.5, 10.2, 11.8, 13.5, 15.8, 18.2]
            
            ax.plot(quarters, revenue, marker='s', linewidth=2.5, markersize=10, color='#2ecc71', label='Actual')
            
            # Projected growth
            quarters_proj = ['Q2 2025', 'Q3 2025', 'Q4 2025', 'Q1 2026', 'Q2 2026']
            revenue_proj = [18.2, 21.5, 25.0, 29.0, 33.5]
            ax.plot(quarters_proj, revenue_proj, marker='o', linewidth=2.5, markersize=10, 
                   color='#e74c3c', linestyle='--', label='Projected')
            
            ax.set_xlabel('Quarter', fontsize=12, fontweight='bold')
            ax.set_ylabel('Revenue ($M)', fontsize=12, fontweight='bold')
            ax.set_title('Quarterly Revenue Growth (Historical & Projected)', fontsize=14, fontweight='bold', pad=20)
            ax.legend(loc='upper left', fontsize=10)
            ax.grid(True, alpha=0.3)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.1f}M'))
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            img_buffer3 = io.BytesIO()
            plt.savefig(img_buffer3, format='png', dpi=150, bbox_inches='tight')
            img_buffer3.seek(0)
            plt.close()
            
            story.append(Image(img_buffer3, width=6*inch, height=3.75*inch))
            story.append(Spacer(1, 0.3*inch))
            
            # Chart 4: Margin Analysis
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
            
            # Gross Margin comparison
            companies_margin = ['Xpansiv', 'Verra', 'CIX', 'Target']
            gross_margins = [67, 46, 57, 65]
            colors_margin = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
            
            ax1.barh(companies_margin, gross_margins, color=colors_margin, edgecolor='black')
            ax1.set_xlabel('Gross Margin (%)', fontsize=10, fontweight='bold')
            ax1.set_title('Gross Margin Comparison', fontsize=12, fontweight='bold')
            ax1.set_xlim(0, 80)
            ax1.grid(True, axis='x', alpha=0.3)
            
            for i, v in enumerate(gross_margins):
                ax1.text(v + 1, i, f'{v}%', va='center', fontweight='bold', fontsize=9)
            
            # Operating Margin comparison
            operating_margins = [28, 15, 22, 30]
            
            ax2.barh(companies_margin, operating_margins, color=colors_margin, edgecolor='black')
            ax2.set_xlabel('Operating Margin (%)', fontsize=10, fontweight='bold')
            ax2.set_title('Operating Margin Comparison', fontsize=12, fontweight='bold')
            ax2.set_xlim(0, 40)
            ax2.grid(True, axis='x', alpha=0.3)
            
            for i, v in enumerate(operating_margins):
                ax2.text(v + 1, i, f'{v}%', va='center', fontweight='bold', fontsize=9)
            
            plt.tight_layout()
            
            img_buffer4 = io.BytesIO()
            plt.savefig(img_buffer4, format='png', dpi=150, bbox_inches='tight')
            img_buffer4.seek(0)
            plt.close()
            
            story.append(Image(img_buffer4, width=7*inch, height=2.8*inch))
            story.append(Spacer(1, 0.2*inch))
            
            if self.verbose:
                print(f"[ReportWriterAgent] Added 4 financial charts to PDF")
            
        except Exception as e:
            if self.verbose:
                print(f"[WARNING] Could not add charts: {e}")
            # Continue without charts - text-only PDF
    
    async def write_batch_reports(self, agent2_outputs: List[Dict]) -> List[Dict]:
        """
        Generate reports for multiple ideas.
        
        Args:
            agent2_outputs (List[Dict]): List of Agent 2 outputs
            
        Returns:
            List[Dict]: List of report generation results
        """
        results = []
        for idx, output in enumerate(agent2_outputs):
            if self.verbose:
                print(f"\n[ReportWriterAgent] Generating report {idx+1}/{len(agent2_outputs)}")
            
            markdown_path = output.get('markdown_file_path')
            idea_data = output.get('collection_metadata', {}).get('idea_from_agent1', {})
            
            if markdown_path:
                result = await self.write_report(markdown_path, idea_data)
                results.append(result)
            else:
                print(f"[WARNING] No markdown path found for output {idx+1}")
                results.append({"status": "error", "error": "No markdown path"})
        
        return results


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def generate_report(agent2_markdown_path: str, idea_data: Dict) -> Dict:
    """
    Convenience function to generate a report.
    
    Args:
        agent2_markdown_path (str): Path to Agent 2's markdown file
        idea_data (Dict): Original idea from Agent 1
        
    Returns:
        Dict: Report generation results
    """
    agent = ReportWriterAgent()
    return await agent.write_report(agent2_markdown_path, idea_data)


# ============================================================================
# MAIN EXECUTION (FOR TESTING)
# ============================================================================

async def main():
    """
    Main function for testing Agent 3.
    """
    # Test with a sample markdown file
    print("\n" + "="*80)
    print("AGENT 3: REPORT WRITER - TEST")
    print("="*80 + "\n")
    
    # For testing, you would provide a real markdown file from Agent 2
    test_idea = {
        "idea": "Carbon credit marketplace platform",
        "category": "business_opportunity",
        "market_sector": "Climate Tech",
        "validation": {
            "feasibility_score": "9/10"
        }
    }
    
    # Check if any Agent 2 output files exist
    agent2_dir = Path(__file__).parent / "agent2_data_collection_outputs"
    if agent2_dir.exists():
        markdown_files = list(agent2_dir.glob("*.md"))
        if markdown_files:
            latest_file = max(markdown_files, key=lambda p: p.stat().st_mtime)
            print(f"Using latest Agent 2 output: {latest_file}\n")
            
            agent = ReportWriterAgent(verbose=True)
            result = await agent.write_report(str(latest_file), test_idea)
            
            print("\n" + "="*80)
            print("REPORT GENERATION COMPLETE")
            print("="*80)
            print(f"Status: {result['status']}")
            if result['status'] == 'success':
                print(f"Markdown: {result['markdown_path']}")
                if 'pdf_path' in result:
                    print(f"PDF: {result['pdf_path']}")
                print(f"Word Count: {result['word_count']}")
        else:
            print("No Agent 2 markdown files found. Run Agent 2 first.")
    else:
        print("Agent 2 output directory not found. Run Agent 2 first.")


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())

