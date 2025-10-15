"""
Agent 2: Data Collector Agent

This agent is the second step in the multi-agent investment pipeline. It:
1. Takes extracted ideas from Agent 1 as input
2. Collects comprehensive financial data from authoritative sources
3. Uses Perplexity Sonar Pro with DEEP RESEARCH mode
4. Gathers extensive information WITHOUT analysis or summarization
5. Provides raw data and insights for Agent 3 (Report Writer)

Key Sources Prioritized:
- SEC Edgar (https://www.sec.gov/)
- SEDAR+ (https://www.sedarplus.ca)
- Buyside Digest (https://www.buysidedigest.com/)
- Bloomberg, Reuters, Financial Times
- Industry-specific databases
- Company investor relations
- Market research reports

Architecture:
- Uses Perplexity Sonar Pro model for deep web research
- RESEARCH MODE enabled for comprehensive data gathering
- No analysis - pure data collection for downstream agents
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

# Import agents framework components
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("EXAMPLE_BASE_URL") or "https://api.perplexity.ai"
API_KEY = os.getenv("EXAMPLE_API_KEY")
MODEL_NAME = "sonar-pro"  # Force Sonar Pro for deep research

# Validate configuration
if not API_KEY:
    raise ValueError("EXAMPLE_API_KEY not found. Please set it in your .env file.")

# Initialize client
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)


# ============================================================================
# COMPREHENSIVE FINANCIAL DATA SOURCES
# ============================================================================

FINANCIAL_DATA_SOURCES = {
    "regulatory_filings": [
        "SEC Edgar - https://www.sec.gov/edgar",
        "SEDAR+ (Canada) - https://www.sedarplus.ca",
        "Companies House (UK) - https://www.gov.uk/government/organisations/companies-house",
        "ASIC (Australia) - https://asic.gov.au",
        "FCA (UK) - https://www.fca.org.uk"
    ],
    "institutional_investment": [
        "Buyside Digest - https://www.buysidedigest.com/",
        "13F Filings Tracker - https://whalewisdom.com/",
        "Institutional Investor Magazine - https://www.institutionalinvestor.com/",
        "Preqin (Private Equity) - https://www.preqin.com/",
        "PitchBook - https://pitchbook.com/"
    ],
    "market_data": [
        "Bloomberg Terminal",
        "Reuters Eikon/Refinitiv",
        "FactSet",
        "S&P Capital IQ",
        "Morningstar Direct"
    ],
    "financial_news": [
        "Financial Times - https://www.ft.com/",
        "Wall Street Journal - https://www.wsj.com/",
        "Bloomberg News - https://www.bloomberg.com/",
        "Reuters - https://www.reuters.com/",
        "CNBC - https://www.cnbc.com/"
    ],
    "research_reports": [
        "Gartner Research",
        "Forrester Research",
        "McKinsey Insights",
        "BCG Perspectives",
        "Deloitte Insights"
    ],
    "industry_databases": [
        "IBISWorld - Industry Market Research",
        "Statista - Statistics Portal",
        "Grand View Research",
        "Markets and Markets",
        "Research and Markets"
    ],
    "venture_capital": [
        "Crunchbase - https://www.crunchbase.com/",
        "CB Insights - https://www.cbinsights.com/",
        "VentureBeat - https://venturebeat.com/",
        "TechCrunch - https://techcrunch.com/",
        "Angel List - https://angel.co/"
    ],
    "company_specific": [
        "Investor Relations websites",
        "Annual Reports (10-K, 20-F)",
        "Quarterly Earnings (10-Q)",
        "Proxy Statements (DEF 14A)",
        "8-K Current Reports"
    ],
    "market_intelligence": [
        "S&P Global Market Intelligence",
        "Moody's Analytics",
        "Fitch Ratings",
        "Credit Suisse HOLT",
        "Capital IQ"
    ],
    "alternative_data": [
        "Sensor Tower (App Analytics)",
        "SimilarWeb (Web Traffic)",
        "App Annie",
        "Second Measure (Transaction Data)",
        "Thinknum Alternative Data"
    ]
}


# ============================================================================
# DATA COLLECTOR AGENT CLASS
# ============================================================================

class DataCollectorAgent:
    """
    Agent 2: Collects comprehensive financial data without analysis.
    
    This agent takes ideas from Agent 1 and performs DEEP RESEARCH to gather
    extensive financial information from authoritative sources. It does NOT
    analyze or summarize - it collects raw data for Agent 3 (Report Writer).
    """
    
    def __init__(self, model_name: str = MODEL_NAME, verbose: bool = True):
        """
        Initialize the Data Collector Agent.
        
        Args:
            model_name (str): Perplexity model (forced to sonar-pro)
            verbose (bool): Enable detailed logging
        """
        self.model_name = model_name
        self.verbose = verbose
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the agent with deep research instructions."""
        
        instructions = """
        You are a professional financial data collector for an investment banking firm's analyst department.
        You have access to real-time web search through Perplexity Sonar Pro capabilities.
        
        ⚠️ CRITICAL: YOU ARE IN DEEP RESEARCH MODE ⚠️
        
        TARGET OUTPUT: MINIMUM 10,000 WORDS (approximately 60-80 KB of text)
        TARGET SOURCES: MINIMUM 50-100 DISTINCT AUTHORITATIVE SOURCES
        
        Your PRIMARY TASK:
        Collect EXTREMELY comprehensive, detailed financial information about the given business/investment idea.
        You are NOT to analyze, summarize, or provide opinions. You are ONLY collecting RAW DATA.
        
        EVERY PIECE OF INFORMATION YOU FIND MUST BE:
        - Extracted verbatim (copy exact text from sources)
        - Fully cited with complete URLs
        - Accompanied by all context (dates, numbers, quotes, methodology)
        - Organized by source type for easy reference
        
        ═══════════════════════════════════════════════════════════════
        REQUIRED DATA SOURCES (SEARCH EXHAUSTIVELY):
        ═══════════════════════════════════════════════════════════════
        
        1. REGULATORY FILINGS (SEARCH EXTENSIVELY):
           PRIMARY:
           - SEC Edgar (www.sec.gov/edgar) - 10-K, 10-Q, 8-K, DEF 14A, S-1, 424B
           - SEDAR+ (www.sedarplus.ca) - All Canadian filings
           - Companies House UK (www.gov.uk/government/organisations/companies-house)
           - ASIC Australia (asic.gov.au)
           - FCA UK (www.fca.org.uk)
           
           SEARCH FOR EACH COMPANY:
           - Annual reports (10-K, 20-F) - Extract EVERY financial table
           - Quarterly reports (10-Q) - Last 8 quarters minimum
           - Current reports (8-K) - All material events
           - Proxy statements (DEF 14A) - Executive compensation, governance
           - IPO filings (S-1) if applicable
           - Amendment filings
           
           EXTRACT VERBATIM:
           - Complete financial statements (balance sheet, P&L, cash flow)
           - Management Discussion & Analysis (MD&A) - FULL TEXT
           - Risk factors - LIST EVERY SINGLE ONE
           - Business description - COMPLETE SECTION
           - Executive compensation tables
           - Related party transactions
           - Segment reporting
           - Geographic revenue breakdown
           - Customer concentration
           - Debt covenants and terms
        
        2. INSTITUTIONAL INVESTMENT DATA (COMPREHENSIVE):
           - Buyside Digest (www.buysidedigest.com) - ALL articles
           - 13F filings (SEC Edgar) - Top 50 institutional holders
           - Whale Wisdom (whalewisdom.com) - Historical positions
           - Institutional Investor Magazine - ALL mentions
           - Preqin (preqin.com) - Private equity data
           - PitchBook (pitchbook.com) - VC data
           - Hedge Fund Research - Holdings data
           - Morningstar - Mutual fund holdings
           
           FOR EACH HOLDER, EXTRACT:
           - Institution name and type
           - Shares held (current and historical)
           - Percentage of company
           - Dollar value of position
           - Change from previous quarter
           - Filing date
           - Portfolio weight
           - Any public statements or letters
        
        3. MARKET RESEARCH (EXHAUSTIVE COLLECTION):
           INDUSTRY DATABASES (search all):
           - IBISWorld - Industry reports
           - Statista - Statistics and data
           - Grand View Research - Market reports
           - Markets and Markets - Forecasts
           - Research and Markets - Industry analysis
           - Frost & Sullivan - Market intelligence
           - Technavio - Technology markets
           - Gartner - Tech research
           - Forrester - Business research
           - IDC - Market intelligence
           - McKinsey - Industry insights
           - BCG - Perspectives
           - Bain - Industry analysis
           - Deloitte Insights - Sector reports
           - PwC - Industry publications
           - KPMG - Market analysis
           - EY - Sector insights
           
           FOR EACH REPORT, EXTRACT VERBATIM:
           - Report title and date
           - Market size (TAM/SAM/SOM) with years
           - Growth rates (CAGR) with projections
           - Market segmentation data
           - Competitive landscape analysis
           - Key players and market shares
           - Industry trends and drivers
           - Regional analysis
           - Technology trends
           - Regulatory environment
           - Pricing analysis
           - Value chain analysis
           - Porter's Five Forces if available
           - SWOT analysis if available
        
        4. FINANCIAL NEWS (COMPREHENSIVE COVERAGE):
           TIER 1 SOURCES (search all):
           - Bloomberg - ALL articles
           - Reuters - ALL articles
           - Financial Times - ALL articles
           - Wall Street Journal - ALL articles
           - CNBC - ALL articles
           - MarketWatch - ALL articles
           - Business Insider - ALL relevant
           - Forbes - ALL mentions
           - Fortune - ALL mentions
           - Barron's - ALL coverage
           - The Economist - ALL mentions
           
           TIME RANGES TO SEARCH:
           - Last 7 days
           - Last 30 days
           - Last 90 days
           - Last 12 months
           - Historical (if major events)
           
           FOR EACH ARTICLE, EXTRACT:
           - Full headline
           - Publication date and time
           - Author name
           - ALL key facts and figures
           - ALL quotes (verbatim)
           - ALL financial data mentioned
           - ALL analysis from journalists (labeled as such)
           - Related companies mentioned
           - Context and background
        
        5. VENTURE CAPITAL & FUNDING (COMPLETE HISTORY):
           - Crunchbase (crunchbase.com) - FULL profile
           - PitchBook (pitchbook.com) - COMPLETE data
           - CB Insights (cbinsights.com) - ALL analysis
           - VentureBeat - ALL articles
           - TechCrunch - ALL coverage
           - Angel List - Profile data
           - VC databases - Historical rounds
           - Press releases - Funding announcements
           
           FOR EACH FUNDING ROUND, EXTRACT:
           - Round type (Seed/Series A/B/C/D/E/F/etc)
           - Amount raised (USD)
           - Valuation (pre-money and post-money)
           - Date of round
           - Lead investors
           - All participating investors
           - Use of funds (if disclosed)
           - Terms (if available)
           - Board seats
           - Any quotes from founders/investors
           - Press release text
           - News coverage
        
        6. COMPANY-SPECIFIC DATA (EXHAUSTIVE):
           INVESTOR RELATIONS:
           - IR website - ALL content
           - Annual reports - COMPLETE TEXT of last 5 years
           - Quarterly earnings - Last 8 quarters FULL TRANSCRIPTS
           - Earnings presentations - ALL slides verbatim
           - Investor presentations - COMPLETE CONTENT
           - Webcasts - Key quotes and data
           - Press releases - ALL in last 2 years
           - SEC filings - Already covered above
           - Shareholder letters - FULL TEXT
           - Strategic updates - COMPLETE
           - Product launches - ALL details
           
           FINANCIAL STATEMENTS (EXTRACT EVERY LINE ITEM):
           Income Statement:
           - Revenue (by segment, geography, product)
           - Cost of revenue
           - Gross profit and margin
           - Operating expenses (R&D, S&M, G&A)
           - Operating income
           - Interest income/expense
           - Tax provision
           - Net income
           - EPS (basic and diluted)
           - Share count
           
           Balance Sheet:
           - Cash and equivalents
           - Short-term investments
           - Accounts receivable
           - Inventory
           - Total current assets
           - PP&E
           - Intangibles
           - Goodwill
           - Total assets
           - Current liabilities
           - Long-term debt
           - Total liabilities
           - Shareholder equity
           - Book value per share
           
           Cash Flow Statement:
           - Operating cash flow
           - CapEx
           - Free cash flow
           - Investing activities
           - Financing activities
           - Net change in cash
           
           KEY METRICS:
           - Revenue growth (QoQ, YoY)
           - Margin trends
           - Customer metrics (CAC, LTV, retention)
           - Unit economics
           - Operating leverage
           - Return on equity/assets
           - Debt ratios
           - Liquidity ratios
        
        7. COMPETITOR ANALYSIS (DETAILED):
           For EVERY major competitor, collect:
           - Company name and description
           - Founding date and history
           - Revenue and growth
           - Funding history
           - Market position
           - Product offerings
           - Pricing
           - Customer base
           - Geographic presence
           - Technology stack (if available)
           - Competitive advantages
           - Recent news
           - Strategic initiatives
           - Partnerships
           - M&A activity
        
        8. ALTERNATIVE DATA (COMPREHENSIVE):
           - SimilarWeb - Web traffic (last 12 months)
           - Sensor Tower - App data (if applicable)
           - App Annie - Mobile analytics
           - Google Trends - Search interest
           - Glassdoor - Employee reviews and data
           - LinkedIn - Employee count and growth
           - Twitter/X - Social sentiment
           - Reddit - Community discussions
           - Product Hunt - Product launches
           - G2/Capterra - Software reviews
           - Trustpilot - Customer reviews
           - BBB - Customer complaints
           - Patent databases - Innovation activity
           - Academic papers - Research citations
        
        ═══════════════════════════════════════════════════════════════
        RESEARCH PROCESS (FOLLOW EXACTLY):
        ═══════════════════════════════════════════════════════════════
        
        1. IDENTIFY all companies, competitors, and related entities
        2. SEARCH each data source category SYSTEMATICALLY
        3. For EACH source found:
           - Note the source name and type
           - Record the COMPLETE URL
           - Extract information VERBATIM (no paraphrasing)
           - Include ALL context (dates, methodology, disclaimers)
           - Preserve ALL numbers and data points
           - Copy ALL relevant quotes word-for-word
        4. ORGANIZE by source category
        5. COUNT total sources to ensure 50-100+
        6. VERIFY output is 10,000+ words
        
        OUTPUT FORMAT (strict JSON):
        {
            "idea_summary": "Brief restatement of the idea being researched",
            "data_collection": {
                "regulatory_filings": [
                    {
                        "source": "SEC Edgar",
                        "url": "full URL",
                        "document_type": "10-K, 10-Q, 8-K, etc.",
                        "filing_date": "YYYY-MM-DD",
                        "key_information": "EXTENSIVE verbatim excerpts - minimum 500 words per filing. Include: complete business description, full MD&A discussion, all risk factors listed, complete financial tables, segment analysis, geographic breakdown, management commentary, forward-looking statements, and any other material information. COPY TEXT VERBATIM - do not summarize.",
                        "financial_metrics": {
                            "revenue": "Full breakdown by year/quarter/segment/geography with exact figures",
                            "profit_margin": "Gross, operating, net margins with trends",
                            "debt_equity_ratio": "Current and historical with breakdown",
                            "cash_position": "Cash, equivalents, investments with details",
                            "revenue_growth": "QoQ and YoY percentages",
                            "operating_expenses": "R&D, Sales & Marketing, G&A breakdown",
                            "customer_metrics": "If disclosed: CAC, LTV, retention, churn",
                            "other_metrics": "All other disclosed metrics with context"
                        },
                        "management_quotes": "Any verbatim quotes from management about strategy, outlook, risks",
                        "risk_factors_full_list": ["Complete list of every risk factor mentioned"],
                        "segment_data": "Detailed breakdown if multi-segment company",
                        "geographic_data": "Revenue by region if disclosed"
                    }
                    // REPEAT FOR MULTIPLE FILINGS - Target 10-20 regulatory filings
                ],
                "institutional_holdings": [
                    {
                        "source": "13F Filing via SEC Edgar / Whale Wisdom / Buyside Digest",
                        "url": "full URL to filing or article",
                        "holder_name": "Complete institution name and type (hedge fund/mutual fund/pension/etc)",
                        "shares_held": "Exact number of shares",
                        "percentage_ownership": "Exact percentage of outstanding",
                        "dollar_value": "Market value of position",
                        "change_from_previous": "Shares and percentage change from prior quarter",
                        "filing_date": "YYYY-MM-DD",
                        "portfolio_weight": "Percentage of institution's total portfolio",
                        "historical_positions": "Last 4 quarters of holdings if available",
                        "details": "FULL TEXT from source - include any commentary, analysis, or context about why institution holds this position, any activist activity, board representation, etc. Extract verbatim.",
                        "related_activity": "Any news about this holder's activity, letters to management, proxy fights, etc."
                    }
                    // REPEAT FOR TOP 20-30 INSTITUTIONAL HOLDERS
                ],
                "market_research": [
                    {
                        "source": "Research firm name (IBISWorld, Statista, Grand View, etc)",
                        "url": "full URL",
                        "report_title": "Complete report title",
                        "publication_date": "YYYY-MM-DD",
                        "report_code": "Report ID/SKU if available",
                        "page_count": "Number of pages",
                        "key_findings": "EXTENSIVE extraction - minimum 300-500 words per report. Include: executive summary verbatim, all market size figures, growth projections, segment analysis, regional breakdown, competitive landscape, key trends, drivers and restraints, opportunities and challenges, technology trends, regulatory environment, value chain analysis, pricing trends. COPY VERBATIM.",
                        "market_size": "TAM/SAM/SOM with exact figures, currency, and years. Include historical (last 5 years) and projected (next 5-10 years)",
                        "growth_projections": "CAGR with base year, forecast period, and methodology. Include different scenarios if provided",
                        "market_segmentation": "By product type, application, end-user, geography - all with size and growth data",
                        "regional_analysis": "Detailed breakdown by region/country with market sizes and growth rates",
                        "competitive_analysis": "Market share data, competitive positioning, key players with descriptions",
                        "key_players": "List of top 10-20 companies with brief profiles",
                        "industry_trends": "All major trends discussed in detail",
                        "drivers_and_restraints": "Complete lists with explanations",
                        "opportunities": "Investment opportunities and market gaps identified",
                        "challenges": "Barriers to entry and market challenges",
                        "regulatory_environment": "Key regulations impacting the market",
                        "technology_trends": "Emerging technologies and their impact",
                        "methodology": "How the research was conducted",
                        "data_sources": "Primary and secondary sources used"
                    }
                    // REPEAT FOR 15-25 MARKET RESEARCH REPORTS
                ],
                "financial_news": [
                    {
                        "source": "Bloomberg/Reuters/FT/WSJ/CNBC/etc",
                        "url": "full URL",
                        "headline": "Complete headline and subheadline",
                        "author": "Article author name",
                        "publication_date": "YYYY-MM-DD HH:MM",
                        "article_text": "EXTENSIVE extraction - minimum 200-300 words per article. Extract ALL key paragraphs verbatim, especially those containing facts, figures, quotes, and context. Include: main story, background, all financial data mentioned, company responses, analyst opinions (labeled as such), market reaction, related developments.",
                        "key_facts": "Bullet list of every fact mentioned",
                        "relevant_figures": "ALL numbers mentioned with full context",
                        "executive_quotes": "All verbatim quotes from company executives with their titles",
                        "analyst_quotes": "All verbatim quotes from analysts with their firms",
                        "market_data": "Stock price, trading volume, market cap if mentioned",
                        "related_companies": "Other companies mentioned in article",
                        "context": "Background information and prior developments mentioned"
                    }
                    // REPEAT FOR 20-40 NEWS ARTICLES across different time periods
                ],
                "funding_and_valuations": [
                    {
                        "source": "Crunchbase/PitchBook/CB Insights/TechCrunch/Press Release",
                        "url": "full URL",
                        "company_name": "Full company name",
                        "funding_round": "Seed/Series A/B/C/D/E/F/Growth/etc",
                        "amount_raised": "Exact USD amount",
                        "valuation": "Pre-money and post-money valuation with sources",
                        "date": "YYYY-MM-DD",
                        "lead_investors": ["Primary lead investor(s)"],
                        "participating_investors": ["Complete list of all investors"],
                        "new_board_members": "If disclosed",
                        "use_of_funds": "Detailed explanation of how funds will be used - extract verbatim from press release",
                        "terms": "Liquidation preferences, voting rights, etc if disclosed",
                        "previous_rounds": "History of all prior funding with amounts and dates",
                        "total_raised_to_date": "Cumulative funding",
                        "press_release_text": "FULL TEXT of official press release if available - minimum 200 words",
                        "founder_quotes": "All verbatim quotes from founders with their titles",
                        "investor_quotes": "All verbatim quotes from investors explaining investment thesis",
                        "news_coverage": "Summary of how major publications covered the round",
                        "context": "Market conditions, company milestones, competitive positioning at time of round"
                    }
                    // REPEAT FOR ALL FUNDING ROUNDS - Target 5-15 rounds depending on company stage
                ],
                "company_data": [
                    {
                        "source": "Company Investor Relations / Annual Report / Earnings Release",
                        "url": "full URL",
                        "document_type": "10-K/Annual Report/Earnings Release/Investor Presentation",
                        "fiscal_period": "FY 2024 / Q3 2025 / etc",
                        "date_published": "YYYY-MM-DD",
                        "financial_statements": "COMPLETE EXTRACTION - minimum 400-600 words. Include every line item from: Income Statement (revenue by segment, COGS, gross profit, R&D, S&M, G&A, operating income, interest, taxes, net income, EPS), Balance Sheet (all asset categories, all liability categories, equity), Cash Flow Statement (operating CF, investing CF, financing CF, free cash flow). Include multiple periods for trend analysis.",
                        "management_commentary": "EXTENSIVE verbatim excerpts - minimum 300-400 words. Extract CEO/CFO commentary on: business performance, market conditions, strategic initiatives, outlook, guidance, product launches, partnerships, M&A, capital allocation, shareholder returns. Include full context.",
                        "risk_factors": "COMPLETE LIST - extract every single risk factor mentioned with full descriptions",
                        "business_description": "FULL DESCRIPTION - minimum 200-300 words covering: what company does, products/services, target markets, competitive advantages, business model, revenue streams, go-to-market strategy, geographic presence",
                        "key_metrics": "All KPIs reported: user growth, retention, ARR, bookings, backlog, margins, operating leverage, etc with trends",
                        "guidance": "Management guidance for future periods with assumptions",
                        "capital_structure": "Shares outstanding, dilution, debt levels, covenants",
                        "shareholder_information": "Ownership structure, insider holdings, buybacks, dividends",
                        "strategic_initiatives": "Major projects, investments, expansions discussed",
                        "competitive_positioning": "How management describes competitive landscape",
                        "customer_information": "Major customers, concentration, win rates if disclosed"
                    }
                    // REPEAT FOR MULTIPLE PERIODS - Target 8-12 quarterly/annual reports
                ],
                "alternative_data": [
                    {
                        "source": "SimilarWeb/Sensor Tower/App Annie/LinkedIn/Glassdoor/etc",
                        "url": "full URL",
                        "data_type": "Web Traffic/App Downloads/Employee Data/Reviews/etc",
                        "metric_type": "Specific metrics tracked",
                        "current_values": "Most recent numbers with date",
                        "historical_values": "Last 12 months of data points",
                        "time_period": "Date range covered",
                        "growth_trends": "Month-over-month and year-over-year growth rates",
                        "geographic_breakdown": "Traffic/users by country if available",
                        "demographic_data": "User demographics if available",
                        "engagement_metrics": "Time on site, pages per visit, bounce rate, etc",
                        "technology_stack": "If available from BuiltWith or similar",
                        "employee_data": "LinkedIn headcount, growth rate, locations, functions",
                        "glassdoor_data": "Rating, review count, CEO approval, top pros/cons from reviews",
                        "social_metrics": "Twitter followers, engagement, Reddit mentions, etc",
                        "details": "EXTENSIVE context - minimum 150-200 words per source. Extract all available data points verbatim."
                    }
                    // REPEAT FOR 10-20 ALTERNATIVE DATA SOURCES
                ],
                "competitor_analysis": [
                    {
                        "competitor_name": "Full company name",
                        "competitor_profile": "COMPREHENSIVE profile - minimum 300 words. Include: founding story, business model, products/services, target market, competitive advantages, weaknesses, recent developments, strategic direction",
                        "financial_data": "All available financial metrics",
                        "funding_history": "Complete funding rounds",
                        "market_position": "Market share, positioning, customer base",
                        "recent_news": "All major news from last 12 months",
                        "sources": ["All URLs for this competitor data"]
                    }
                    // REPEAT FOR TOP 10-15 COMPETITORS
                ]
            },
            "sources_summary": {
                "total_sources": "MUST BE 50-100+",
                "regulatory_filings_count": "number",
                "institutional_holdings_count": "number",
                "market_research_reports_count": "number",
                "news_articles_count": "number",
                "funding_sources_count": "number",
                "company_documents_count": "number",
                "alternative_data_count": "number",
                "competitor_sources_count": "number",
                "all_urls": ["Complete list of ALL 50-100+ URLs cited"]
            },
            "collection_metadata": {
                "idea_from_agent1": "Original idea passed from Agent 1",
                "collection_timestamp": "ISO timestamp",
                "sources_searched": "Comprehensive list of all databases/sites searched",
                "data_completeness": "Detailed assessment of data availability and gaps",
                "word_count": "Approximate word count - VERIFY THIS IS 10,000+",
                "source_count": "Total sources - VERIFY THIS IS 50-100+"
            }
        }
        
        ═══════════════════════════════════════════════════════════════
        ⚠️⚠️⚠️ CRITICAL REQUIREMENTS - MUST FOLLOW ⚠️⚠️⚠️
        ═══════════════════════════════════════════════════════════════
        
        1. OUTPUT LENGTH: MINIMUM 10,000 WORDS
           - This is approximately 60-80 KB of text
           - Each regulatory filing: 500+ words
           - Each market research report: 300-500 words
           - Each news article: 200-300 words
           - Each company report: 400-600 words
           - DO NOT STOP until you hit 10,000+ words
        
        2. SOURCE COUNT: MINIMUM 50-100 DISTINCT SOURCES
           - Regulatory filings: 10-20
           - Institutional holdings: 20-30
           - Market research: 15-25
           - News articles: 20-40
           - Funding sources: 5-15
           - Company documents: 8-12
           - Alternative data: 10-20
           - Competitor sources: 10-15
           - VERIFY source count meets minimum
        
        3. USE RESEARCH MODE
           - Conduct EXHAUSTIVE searches across ALL source categories
           - Search multiple time periods (last 7 days, 30 days, 90 days, 12 months)
           - Search multiple databases for each category
           - Leave no stone unturned
        
        4. PRIORITIZE PRIMARY SOURCES
           - SEC filings (10-K, 10-Q, 8-K, DEF 14A)
           - SEDAR+ filings
           - Company IR websites
           - Official press releases
           - Regulatory announcements
           - THEN secondary sources (news, research reports)
        
        5. EXTRACT VERBATIM - NO ANALYSIS
           - Copy exact text from sources
           - Preserve ALL context and methodology
           - Include ALL numbers, dates, names
           - Quote management/analysts word-for-word
           - DO NOT paraphrase or summarize
           - DO NOT provide opinions or analysis
           - DO NOT make recommendations
        
        6. CITE EVERYTHING
           - Provide FULL URLs for every source
           - Include publication dates
           - Include author names when available
           - Include document types and reference numbers
           - Make it easy to verify every fact
        
        7. ORGANIZE BY SOURCE TYPE
           - Use the exact structure provided above
           - Keep regulatory filings separate from news
           - Keep primary sources separate from secondary
           - This helps Agent 3 (Report Writer) navigate the data
        
        8. IF DATA UNAVAILABLE
           - Explicitly state "Not found" or "Not applicable"
           - Explain why (e.g., "Private company - no SEC filings")
           - Search alternative sources
           - Never leave fields blank without explanation
        
        9. QUALITY OVER SPEED
           - Better to spend 2-3 minutes and get 10,000 words
           - Than to rush and produce 2,000 words
           - Agent 3 NEEDS comprehensive data for analysis
           - Investment boutiques require thorough due diligence
        
        10. VERIFY BEFORE SUBMITTING
            - Count your sources: 50-100+? ✓
            - Estimate word count: 10,000+? ✓
            - All URLs provided? ✓
            - All data verbatim? ✓
            - No analysis included? ✓
        
        ═══════════════════════════════════════════════════════════════
        REMEMBER: You are collecting RAW DATA for a financial analyst.
        The analyst (Agent 3) will do the analysis. Your job is to give
        them as much high-quality source material as possible.
        
        MORE IS BETTER. COMPREHENSIVE IS BETTER. VERBOSE IS BETTER.
        ═══════════════════════════════════════════════════════════════
        """
        
        self.agent = Agent(
            name="DataCollectorAgent",
            instructions=instructions,
            model=OpenAIChatCompletionsModel(
                model=self.model_name,
                openai_client=client
            )
        )
    
    async def collect_data(self, idea_data: Dict, source: str = "agent1", save_markdown: bool = True) -> Dict:
        """
        Collect comprehensive financial data for an idea from Agent 1.
        
        Args:
            idea_data (Dict): Idea data from Agent 1 (single idea object)
            source (str): Source identifier
            save_markdown (bool): Save output as markdown file for Agent 3
            
        Returns:
            Dict: Comprehensive data collection results with markdown_file_path if saved
        """
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"[DataCollectorAgent] Starting deep research collection")
            print(f"[DataCollectorAgent] Idea: {idea_data.get('idea', 'Unknown')[:100]}...")
            print(f"{'='*80}\n")
        
        try:
            # Construct comprehensive research query
            research_query = self._build_research_query(idea_data)
            
            if self.verbose:
                print(f"[DataCollectorAgent] Research query prepared")
                print(f"[DataCollectorAgent] Initiating DEEP RESEARCH mode...")
                print(f"[DataCollectorAgent] This may take 60-120 seconds...\n")
            
            # Run the agent with deep research
            result = await Runner.run(self.agent, research_query)
            
            if self.verbose:
                print(f"\n[DataCollectorAgent] Data collection complete")
                print(f"[DataCollectorAgent] Response length: {len(result.final_output)} characters\n")
            
            # Parse and structure the output
            output_data = self._parse_output(result.final_output, idea_data, source)
            
            # Save as markdown if requested
            if save_markdown:
                markdown_path = self._save_as_markdown(output_data, idea_data)
                output_data['markdown_file_path'] = str(markdown_path)
                
                if self.verbose:
                    print(f"[DataCollectorAgent] Markdown saved to: {markdown_path}\n")
            
            return output_data
            
        except Exception as e:
            print(f"[ERROR] DataCollectorAgent failed: {e}")
            return {
                "idea_summary": idea_data.get('idea', 'Unknown'),
                "data_collection": {},
                "error": str(e),
                "collection_metadata": {
                    "idea_from_agent1": idea_data,
                    "collection_timestamp": datetime.now().isoformat(),
                    "status": "error"
                }
            }
    
    def _build_research_query(self, idea_data: Dict) -> str:
        """
        Build a comprehensive research query for the agent.
        
        Args:
            idea_data (Dict): Idea from Agent 1
            
        Returns:
            str: Formatted research query
        """
        idea = idea_data.get('idea', '')
        category = idea_data.get('category', '')
        market_sector = idea_data.get('market_sector', '')
        source_context = idea_data.get('source_context', '')
        
        # Extract company names if mentioned
        companies = self._extract_company_names(idea, source_context)
        
        query = f"""
DEEP RESEARCH REQUEST - COMPREHENSIVE DATA COLLECTION

IDEA TO RESEARCH:
{idea}

CATEGORY: {category}
MARKET SECTOR: {market_sector}
CONTEXT: {source_context}

COMPANIES/ENTITIES IDENTIFIED: {', '.join(companies) if companies else 'To be determined'}

---

RESEARCH INSTRUCTIONS:

You are in DEEP RESEARCH MODE. Conduct exhaustive research across ALL available sources.

1. REGULATORY FILINGS SEARCH:
   - Search SEC Edgar for: {', '.join(companies) if companies else market_sector + ' companies'}
   - Look for: 10-K annual reports, 10-Q quarterly reports, 8-K current reports, DEF 14A proxy statements
   - Also search SEDAR+ for Canadian companies
   - Collect: Financial statements, MD&A sections, risk factors, business descriptions
   - Extract ALL financial metrics: revenue, profit, margins, debt, cash, growth rates
   
2. INSTITUTIONAL HOLDINGS RESEARCH:
   - Search Buyside Digest for recent activity
   - Find 13F filings showing institutional positions
   - Identify: Top holders, recent changes, percentage ownership
   - Look for hedge fund activity, activist investors
   
3. MARKET RESEARCH COLLECTION:
   - Search for industry reports on: {market_sector}
   - Sources: IBISWorld, Statista, Grand View Research, Markets and Markets
   - Collect: Market size (TAM/SAM), growth rates (CAGR), forecasts, trends
   - Get competitive landscape data, market share figures
   
4. FINANCIAL NEWS GATHERING:
   - Search Bloomberg, Reuters, Financial Times, WSJ for recent news (last 90 days)
   - Topics: funding rounds, M&A, earnings, partnerships, product launches
   - Collect: Headlines, dates, key facts, quotes, financial figures
   
5. VENTURE CAPITAL DATA:
   - Search Crunchbase, PitchBook, CB Insights
   - Collect: Funding history, investors, valuations, cap table info
   - Get details on latest rounds, use of funds, investor quotes
   
6. COMPANY-SPECIFIC DATA:
   - Find investor relations websites
   - Collect: Latest earnings reports, investor presentations, webcasts
   - Extract: Financial guidance, strategic initiatives, competitive positioning
   
7. ALTERNATIVE DATA:
   - Search for web traffic data (SimilarWeb)
   - App analytics (Sensor Tower, App Annie)
   - Transaction data, user growth metrics
   - Consumer sentiment, reviews, ratings

FOR EACH SOURCE:
- Provide full URL
- Extract verbatim data points and quotes
- Include all relevant numbers and metrics
- Preserve full context (no summarization)
- Note publication/filing dates

CRITICAL: This is DATA COLLECTION ONLY - no analysis, no opinions, no summarization.
Aim for 50-100+ sources with extensive information from each.

Begin comprehensive research now.
"""
        
        return query
    
    def _extract_company_names(self, idea: str, context: str) -> List[str]:
        """
        Extract potential company names from idea and context.
        
        Args:
            idea (str): Idea description
            context (str): Source context
            
        Returns:
            List[str]: List of potential company names
        """
        # Simple extraction - look for capitalized words that might be company names
        import re
        
        text = f"{idea} {context}"
        
        # Pattern for potential company names (2+ capitalized words or single caps with Inc/Corp/Ltd)
        pattern = r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*(?:\s+(?:Inc|Corp|Corporation|Ltd|Limited|LLC|Group|Partners|Capital|Ventures|Technologies|Systems|Solutions))?\b'
        
        potential_names = re.findall(pattern, text)
        
        # Filter out common words
        common_words = {'The', 'A', 'An', 'This', 'That', 'These', 'Those', 'Market', 'Industry', 'Sector', 'Company', 'Business'}
        
        companies = [name for name in potential_names if name not in common_words and len(name) > 2]
        
        # Remove duplicates and return first 5
        return list(dict.fromkeys(companies))[:5]
    
    def _parse_output(self, output: str, idea_data: Dict, source: str) -> Dict:
        """
        Parse the agent's output into structured format.
        
        Args:
            output (str): Raw output from agent
            idea_data (Dict): Original idea data
            source (str): Source identifier
            
        Returns:
            Dict: Structured data collection output
        """
        # Try to parse as JSON
        try:
            if "{" in output and "}" in output:
                start = output.find("{")
                end = output.rfind("}") + 1
                json_str = output[start:end]
                parsed = json.loads(json_str)
                
                # Add metadata
                if "collection_metadata" not in parsed:
                    parsed["collection_metadata"] = {}
                
                parsed["collection_metadata"].update({
                    "idea_from_agent1": idea_data,
                    "collection_timestamp": datetime.now().isoformat(),
                    "model": self.model_name,
                    "status": "success"
                })
                
                return parsed
        except json.JSONDecodeError:
            pass
        
        # Fallback: return raw output with structure
        return {
            "idea_summary": idea_data.get('idea', 'Unknown'),
            "data_collection": {
                "raw_output": output
            },
            "collection_metadata": {
                "idea_from_agent1": idea_data,
                "collection_timestamp": datetime.now().isoformat(),
                "model": self.model_name,
                "status": "raw_output",
                "note": "Could not parse as JSON, returning raw output"
            }
        }
    
    def _save_as_markdown(self, output_data: Dict, idea_data: Dict) -> Path:
        """
        Save data collection output as markdown file for Agent 3.
        
        Args:
            output_data (Dict): Data collection output
            idea_data (Dict): Original idea from Agent 1
            
        Returns:
            Path: Path to saved markdown file
        """
        # Create output directory
        output_dir = Path(__file__).parent / "agent2_data_collection_outputs"
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        idea_slug = idea_data.get('idea', 'unknown')[:50].replace(' ', '_').replace('/', '_')
        filename = f"data_collection_{timestamp}_{idea_slug}.md"
        filepath = output_dir / filename
        
        # Format as markdown
        markdown_content = self._format_as_markdown(output_data, idea_data)
        
        # Save file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath
    
    def _format_as_markdown(self, output_data: Dict, idea_data: Dict) -> str:
        """
        Format data collection output as markdown.
        
        Args:
            output_data (Dict): Data collection output
            idea_data (Dict): Original idea from Agent 1
            
        Returns:
            str: Markdown formatted content
        """
        md = f"""# Data Collection Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Agent**: Data Collector (Agent 2)  
**For**: Report Writer (Agent 3)

---

## Idea Being Researched

**Idea**: {idea_data.get('idea', 'Unknown')}

**Category**: {idea_data.get('category', 'Unknown')}

**Market Sector**: {idea_data.get('market_sector', 'Unknown')}

**Feasibility Score**: {idea_data.get('validation', {}).get('feasibility_score', 'N/A')}

---

## Data Collection Summary

{output_data.get('idea_summary', 'No summary available')}

---

## Collected Data

"""
        
        # Add all collected data
        data_collection = output_data.get('data_collection', {})
        
        # Handle raw output case
        if 'raw_output' in data_collection:
            md += f"\n### Raw Research Output\n\n{data_collection['raw_output']}\n\n"
        else:
            # Format each section
            for section_name, section_data in data_collection.items():
                if section_name in ['raw_output']:
                    continue
                
                section_title = section_name.replace('_', ' ').title()
                md += f"\n## {section_title}\n\n"
                
                if isinstance(section_data, list):
                    for idx, item in enumerate(section_data, 1):
                        md += f"\n### {section_title} #{idx}\n\n"
                        md += self._format_dict_as_markdown(item, indent=0)
                elif isinstance(section_data, dict):
                    md += self._format_dict_as_markdown(section_data, indent=0)
                else:
                    md += f"{section_data}\n\n"
        
        # Add sources summary
        if 'sources_summary' in output_data:
            md += "\n---\n\n## Sources Summary\n\n"
            md += self._format_dict_as_markdown(output_data['sources_summary'], indent=0)
        
        return md
    
    def _format_dict_as_markdown(self, data: dict, indent: int = 0) -> str:
        """Format dictionary as markdown."""
        md = ""
        indent_str = "  " * indent
        
        for key, value in data.items():
            key_formatted = key.replace('_', ' ').title()
            
            if isinstance(value, dict):
                md += f"{indent_str}**{key_formatted}**:\n"
                md += self._format_dict_as_markdown(value, indent + 1)
            elif isinstance(value, list):
                md += f"{indent_str}**{key_formatted}**:\n"
                for item in value:
                    if isinstance(item, dict):
                        md += self._format_dict_as_markdown(item, indent + 1)
                    else:
                        md += f"{indent_str}- {item}\n"
            else:
                md += f"{indent_str}**{key_formatted}**: {value}\n"
        
        md += "\n"
        return md
    
    async def collect_batch(self, ideas: List[Dict], save_markdown: bool = True) -> List[Dict]:
        """
        Collect data for multiple ideas.
        
        Args:
            ideas (List[Dict]): List of idea objects from Agent 1
            save_markdown (bool): Save outputs as markdown files
            
        Returns:
            List[Dict]: List of data collection results
        """
        results = []
        for idx, idea in enumerate(ideas):
            if self.verbose:
                print(f"\n[DataCollectorAgent] Processing idea {idx+1}/{len(ideas)}")
            
            result = await self.collect_data(idea, save_markdown=save_markdown)
            results.append(result)
        
        return results


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def collect_data_for_idea(idea_data: Dict, source: str = "agent1") -> Dict:
    """
    Convenience function to collect data for a single idea.
    
    Args:
        idea_data (Dict): Idea from Agent 1
        source (str): Source identifier
        
    Returns:
        Dict: Data collection results
    """
    agent = DataCollectorAgent()
    return await agent.collect_data(idea_data, source)


# ============================================================================
# MAIN EXECUTION (FOR TESTING)
# ============================================================================

async def main():
    """
    Main function for testing Agent 2.
    """
    # Example idea from Agent 1
    test_idea = {
        "idea": "AI-powered tutoring platform for STEM subjects",
        "source_context": "EdTech market growing, personalized learning demand",
        "category": "business_opportunity",
        "market_sector": "EdTech",
        "validation": {
            "market_viability": "Strong growth projected",
            "feasibility_score": "9/10"
        }
    }
    
    agent = DataCollectorAgent(verbose=True)
    result = await agent.collect_data(test_idea)
    
    print("\n" + "="*80)
    print("FINAL DATA COLLECTION OUTPUT:")
    print("="*80)
    print(json.dumps(result, indent=2)[:2000])  # First 2000 chars for preview
    print("\n... [output truncated for display] ...")


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())

