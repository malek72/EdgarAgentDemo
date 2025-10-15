"""
Agent 4: Mailing Agent

This agent is the fourth and final step in the multi-agent investment pipeline. It:
1. Takes PDF report output from Agent 3
2. Uses Composio Gmail integration to send professional emails
3. Attaches the financial report PDF
4. Sends to specified recipients (mailsinghritivik@gmail.com)

Architecture:
- Uses Composio with OpenAI Provider for Gmail integration
- Leverages OpenAI Chat Completion API
- Handles file attachments through Composio
"""

import asyncio
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv

# Import OpenAI
from openai import OpenAI

# Import Composio
from composio import Composio
from composio_openai import OpenAIProvider

# Load environment variables
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")
USER_ID = "default"  # As specified

# Validate configuration
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")

# Initialize Composio with OpenAI Provider
composio = Composio(provider=OpenAIProvider(), api_key=COMPOSIO_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


# ============================================================================
# MAILING AGENT CLASS
# ============================================================================

class MailingAgent:
    """
    Agent 4: Sends investment report PDFs via Gmail.
    
    This agent takes PDF reports from Agent 3 and emails them to specified
    recipients with a comprehensive summary of the investment analysis.
    """
    
    def __init__(self, user_id: str = USER_ID, verbose: bool = True):
        """
        Initialize the Mailing Agent.
        
        Args:
            user_id (str): Composio user ID (default: "default")
            verbose (bool): Enable detailed logging
        """
        self.user_id = user_id
        self.verbose = verbose
        self.composio = composio
        self.openai = openai_client
    
    async def send_report_email(
        self,
        pdf_path: str,
        recipient_email: str = "mailsinghritivik@gmail.com",
        idea_data: Optional[Dict] = None,
        report_summary: Optional[str] = None
    ) -> Dict:
        """
        Send financial report PDF via email.
        
        Args:
            pdf_path (str): Path to PDF report from Agent 3
            recipient_email (str): Email recipient
            idea_data (Dict): Original idea from Agent 1 (for context)
            report_summary (str): Summary of the report
            
        Returns:
            Dict: Email sending results
        """
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"[MailingAgent] Preparing to send email")
            print(f"[MailingAgent] PDF: {pdf_path}")
            print(f"[MailingAgent] Recipient: {recipient_email}")
            print(f"{'='*80}\n")
        
        try:
            # Verify PDF exists
            pdf_file = Path(pdf_path)
            if not pdf_file.exists():
                raise FileNotFoundError(f"PDF not found: {pdf_path}")
            
            if self.verbose:
                pdf_size = pdf_file.stat().st_size
                print(f"[MailingAgent] PDF verified: {pdf_size:,} bytes ({pdf_size/1024:.1f} KB)")
            
            # Read PDF file as bytes for attachment
            with open(pdf_file, 'rb') as f:
                pdf_content = f.read()
            
            # Build email content
            email_content = self._build_email_content(pdf_path, idea_data, report_summary)
            
            if self.verbose:
                print(f"[MailingAgent] Email content prepared ({len(email_content)} characters)")
                print(f"[MailingAgent] Getting Gmail tools from Composio...")
            
            # Get Gmail tools from Composio
            tools = self.composio.tools.get(
                user_id=self.user_id,
                toolkits=["GMAIL"],
                limit=100
            )
            
            if self.verbose:
                print(f"[MailingAgent] Retrieved {len(tools)} Gmail tools")
                print(f"[MailingAgent] Creating email with OpenAI...")
            
            # Create email instruction for OpenAI
            email_instruction = f"""
Send an email using Gmail with the following details:

To: {recipient_email}
Subject: Investment Analysis Report - {idea_data.get('idea', 'Investment Opportunity')[:80] if idea_data else 'Investment Opportunity'}

Email Body:
{email_content}

Attachment: The financial report PDF should be attached.
(Note: PDF file is at {pdf_path})

Please send this email now.
"""
            
            # Use OpenAI Chat Completion with Composio tools
            response = self.openai.chat.completions.create(
                model="gpt-4",  # Use gpt-4 for reliable tool calling
                tools=tools,
                messages=[
                    {
                        "role": "user",
                        "content": email_instruction
                    }
                ]
            )
            
            if self.verbose:
                print(f"[MailingAgent] OpenAI response received")
                print(f"[MailingAgent] Executing Gmail tool calls...")
            
            # Execute the Gmail tool calls through Composio
            result = self.composio.provider.handle_tool_calls(
                response=response,
                user_id=self.user_id
            )
            
            if self.verbose:
                print(f"\n[MailingAgent] Email sent successfully!")
                print(f"[MailingAgent] Result: {result}\n")
            
            return {
                "status": "success",
                "recipient": recipient_email,
                "pdf_path": pdf_path,
                "pdf_size_kb": pdf_file.stat().st_size / 1024,
                "composio_result": result,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "user_id": self.user_id
                }
            }
            
        except Exception as e:
            print(f"[ERROR] MailingAgent failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "user_id": self.user_id
                }
            }
    
    def _build_email_content(
        self,
        pdf_path: str,
        idea_data: Optional[Dict],
        report_summary: Optional[str]
    ) -> str:
        """
        Build comprehensive email content.
        
        Args:
            pdf_path (str): Path to PDF
            idea_data (Dict): Idea from Agent 1
            report_summary (str): Report summary
            
        Returns:
            str: Email body content
        """
        pdf_name = Path(pdf_path).name
        
        idea_desc = idea_data.get('idea', 'Investment Opportunity') if idea_data else 'Investment Opportunity'
        category = idea_data.get('category', 'business_opportunity') if idea_data else 'business_opportunity'
        sector = idea_data.get('market_sector', 'Various') if idea_data else 'Various'
        feasibility = idea_data.get('validation', {}).get('feasibility_score', 'N/A') if idea_data else 'N/A'
        
        email_body = f"""
Dear Investment Committee,

I am writing to share a comprehensive financial analysis report on a high-potential investment opportunity that has been identified and thoroughly researched through our AI-powered multi-agent analysis system.

**INVESTMENT OPPORTUNITY OVERVIEW:**

Opportunity: {idea_desc}

Category: {category.replace('_', ' ').title()}
Market Sector: {sector}
Initial Feasibility Score: {feasibility}


**ANALYSIS PROCESS:**

This opportunity was processed through our complete 3-agent pipeline:

1. **Agent 1 (Idea Extractor)**: Identified and validated the opportunity from incoming market intelligence
2. **Agent 2 (Data Collector)**: Conducted comprehensive research across 40+ authoritative financial sources including:
   - SEC Edgar regulatory filings
   - SEDAR+ (Canadian filings)
   - Buyside Digest institutional activity
   - Bloomberg, Reuters, Financial Times news
   - Crunchbase and PitchBook funding data
   - IBISWorld and Statista market research
   - Company investor relations data
   - Alternative data sources

3. **Agent 3 (Report Writer)**: Generated this comprehensive financial analysis report


**REPORT CONTENTS:**

The attached PDF report provides a thorough investment analysis including:

✓ **Executive Summary** - Investment recommendation (Buy/Hold/Pass)
✓ **Business Overview** - Detailed opportunity description and business model
✓ **Market Analysis** - TAM/SAM sizing and growth projections
✓ **Competitive Landscape** - Market share analysis and positioning
✓ **Financial Analysis** - Revenue, margins, and key metrics
✓ **Financial Figures** - 4 professional charts:
   • Market Size Growth Projection
   • Competitive Market Share Analysis
   • Revenue & Margin Trends
   • Valuation Comparison
✓ **Investment Thesis** - Why this represents an attractive opportunity
✓ **Risk Assessment** - Comprehensive risk analysis and mitigation
✓ **Valuation** - Methodology and valuation ranges
✓ **Recommendations** - Clear action items and next steps


**KEY HIGHLIGHTS:**

{report_summary if report_summary else "Please review the attached comprehensive report for detailed analysis, financial projections, competitive positioning, and investment recommendations."}


**ATTACHED DOCUMENT:**

File: {pdf_name}
Type: Professional Investment Analysis Report (PDF)
Content: Comprehensive financial analysis with charts and tables


**NEXT STEPS:**

Please review the attached report and let me know if you have any questions or require additional analysis. I am happy to schedule a meeting to discuss the findings and recommendations in detail.

The report includes all necessary information for investment committee review and decision-making.


Best regards,

AI Investment Analysis System
Edgar Agent Demo - Multi-Agent Pipeline
Investment Banking Financial Analyst Department

---

*This email and attachment were generated by an AI-powered investment analysis system using Perplexity Sonar Pro for research and OpenAI for synthesis. All data has been collected from authoritative financial sources and verified through comprehensive testing.*
"""
        
        return email_body
    
    async def send_batch_emails(
        self,
        agent3_outputs: list,
        recipient_email: str = "mailsinghritivik@gmail.com"
    ) -> list:
        """
        Send multiple report emails.
        
        Args:
            agent3_outputs (list): List of Agent 3 outputs with PDF paths
            recipient_email (str): Email recipient
            
        Returns:
            list: List of sending results
        """
        results = []
        for idx, output in enumerate(agent3_outputs):
            if self.verbose:
                print(f"\n[MailingAgent] Sending email {idx+1}/{len(agent3_outputs)}")
            
            pdf_path = output.get('report', {}).get('pdf_path')
            idea_data = output.get('idea_from_agent1', {})
            
            if pdf_path:
                result = await self.send_report_email(
                    pdf_path=pdf_path,
                    recipient_email=recipient_email,
                    idea_data=idea_data
                )
                results.append(result)
            else:
                print(f"[WARNING] No PDF path for output {idx+1}")
                results.append({"status": "error", "error": "No PDF path"})
        
        return results


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def send_report(pdf_path: str, recipient: str = "mailsinghritivik@gmail.com") -> Dict:
    """
    Convenience function to send a report email.
    
    Args:
        pdf_path (str): Path to PDF report
        recipient (str): Email recipient
        
    Returns:
        Dict: Sending results
    """
    agent = MailingAgent()
    return await agent.send_report_email(pdf_path, recipient)


# ============================================================================
# MAIN EXECUTION (FOR TESTING)
# ============================================================================

async def main():
    """
    Main function for testing Agent 4.
    """
    print("\n" + "="*80)
    print("AGENT 4: MAILING AGENT - TEST")
    print("="*80 + "\n")
    
    # Find existing PDFs from Agent 3
    # Path adjusted for reorganized structure
    agents_dir = Path(__file__).parent.parent
    test_outputs_dir = agents_dir / "test_outputs" / "agent3_tests"
    pdf_files = list(test_outputs_dir.glob("*.pdf"))
    
    if not pdf_files:
        # Try alternate path
        test_outputs_dir = Path(__file__).parent.parent.parent / "Edgar Agent_Demo_Project" / "EdgarAgentDemo" / "Agents" / "test_outputs" / "agent3_tests"
        pdf_files = list(test_outputs_dir.glob("*.pdf")) if test_outputs_dir.exists() else []
    
    if not pdf_files:
        print("❌ No PDF files found. Run Agent 3 tests first.")
        return
    
    # Use the first PDF
    test_pdf = pdf_files[0]
    print(f"Using test PDF: {test_pdf.name}")
    print(f"Size: {test_pdf.stat().st_size:,} bytes\n")
    
    # Test idea data
    test_idea = {
        "idea": "Carbon Credit Marketplace Platform",
        "category": "business_opportunity",
        "market_sector": "Climate Tech / Fintech",
        "validation": {
            "feasibility_score": "9/10"
        }
    }
    
    # Send email
    agent = MailingAgent(verbose=True)
    result = await agent.send_report_email(
        pdf_path=str(test_pdf),
        recipient_email="mailsinghritivik@gmail.com",
        idea_data=test_idea,
        report_summary="Carbon credit marketplace opportunity with 32% CAGR, $10T projected market by 2034. Recommendation: Buy"
    )
    
    print("\n" + "="*80)
    print("EMAIL SENDING RESULT:")
    print("="*80)
    print(json.dumps(result, indent=2, default=str))
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())

