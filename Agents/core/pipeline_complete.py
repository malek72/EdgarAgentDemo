"""
Complete 4-Agent Investment Analysis Pipeline

Agent 1: Idea Extractor - Extract business/investment ideas
Agent 2: Data Collector - Collect comprehensive financial data
Agent 3: Report Writer - Generate professional PDF reports with charts
Agent 4: Mailing Agent - Send reports via Gmail

Flow: Input → Agent 1 → Agent 2 (markdown) → Agent 3 (PDF) → Agent 4 (Email)
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import nest_asyncio

from idea_extractor_agent import IdeaExtractorAgent
from data_collector_agent import DataCollectorAgent
from report_writer_agent import ReportWriterAgent
from mailing_agent import MailingAgent

nest_asyncio.apply()


# ============================================================================
# COMPLETE 4-AGENT PIPELINE
# ============================================================================

class CompleteInvestmentPipeline:
    """
    Complete 4-agent pipeline for investment analysis and distribution.
    
    Agent 1: Extract ideas from unstructured text
    Agent 2: Collect comprehensive financial data
    Agent 3: Write professional analysis report (markdown + PDF)
    Agent 4: Send PDF report via Gmail
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the complete pipeline with all four agents.
        
        Args:
            verbose (bool): Enable detailed logging
        """
        self.verbose = verbose
        self.agent1 = IdeaExtractorAgent(verbose=verbose)
        self.agent2 = DataCollectorAgent(verbose=verbose)
        self.agent3 = ReportWriterAgent(verbose=verbose)
        self.agent4 = MailingAgent(verbose=verbose)
        
        if verbose:
            print("\n" + "="*100)
            print("COMPLETE INVESTMENT ANALYSIS PIPELINE INITIALIZED")
            print("="*100)
            print("Agent 1: Idea Extractor - Ready ✅")
            print("Agent 2: Data Collector - Ready ✅")
            print("Agent 3: Report Writer - Ready ✅")
            print("Agent 4: Mailing Agent - Ready ✅")
            print("="*100 + "\n")
    
    async def process_input(
        self,
        input_text: str,
        source: str = "unknown",
        recipient_email: str = "mailsinghritivik@gmail.com",
        max_ideas_to_research: int = 1,
        max_reports_to_generate: int = 1,
        send_email: bool = True
    ) -> Dict:
        """
        Process input through complete 4-agent pipeline.
        
        Args:
            input_text (str): Raw input (email, WhatsApp, tweet)
            source (str): Source type
            recipient_email (str): Email recipient for reports
            max_ideas_to_research (int): Max ideas for Agent 2
            max_reports_to_generate (int): Max reports for Agent 3
            send_email (bool): Whether to send email via Agent 4
            
        Returns:
            Dict: Complete pipeline results
        """
        pipeline_start = datetime.now()
        
        if self.verbose:
            print(f"\n{'='*100}")
            print(f"COMPLETE PIPELINE EXECUTION STARTED (4 AGENTS)")
            print(f"{'='*100}")
            print(f"Source: {source}")
            print(f"Input length: {len(input_text)} characters")
            print(f"Recipient: {recipient_email}")
            print(f"Send Email: {send_email}")
            print(f"Timestamp: {pipeline_start.isoformat()}")
            print(f"{'='*100}\n")
        
        # =========================================================================
        # STAGE 1: IDEA EXTRACTION (Agent 1)
        # =========================================================================
        
        if self.verbose:
            print(f"\n{'─'*100}")
            print(f"STAGE 1: IDEA EXTRACTION (Agent 1)")
            print(f"{'─'*100}\n")
        
        agent1_start = datetime.now()
        
        try:
            agent1_result = await self.agent1.extract_ideas(input_text, source)
            agent1_duration = (datetime.now() - agent1_start).total_seconds()
            
            if self.verbose:
                ideas_count = len(agent1_result.get('ideas_found', []))
                print(f"\n✅ Agent 1 Complete")
                print(f"   Ideas extracted: {ideas_count}")
                print(f"   Confidence: {agent1_result.get('confidence', 'unknown')}")
                print(f"   Duration: {agent1_duration:.2f}s\n")
        
        except Exception as e:
            print(f"\n❌ Agent 1 Failed: {e}\n")
            return self._create_error_result("failed_at_agent1", str(e), agent1_start, pipeline_start)
        
        # Validate Agent 1 output
        ideas = agent1_result.get('ideas_found', [])
        confidence = agent1_result.get('confidence', 'low')
        
        if not ideas or confidence == 'low':
            if self.verbose:
                print(f"\n⚠️  No actionable ideas - stopping pipeline\n")
            
            return self._create_result("no_actionable_ideas", agent1_result, [], [], [], 
                                      agent1_duration, 0, 0, 0, pipeline_start)
        
        # =========================================================================
        # STAGE 2: DATA COLLECTION (Agent 2)
        # =========================================================================
        
        if self.verbose:
            print(f"\n{'─'*100}")
            print(f"STAGE 2: DATA COLLECTION (Agent 2)")
            print(f"{'─'*100}\n")
        
        ideas_to_research = ideas[:max_ideas_to_research]
        agent2_results = []
        agent2_start = datetime.now()
        
        for idx, idea in enumerate(ideas_to_research):
            if self.verbose:
                print(f"\n   Researching Idea {idx+1}/{len(ideas_to_research)}:")
                print(f"   '{idea.get('idea', 'Unknown')[:80]}...'\n")
            
            try:
                data_collection = await self.agent2.collect_data(
                    idea_data=idea,
                    source="agent1",
                    save_markdown=True
                )
                
                agent2_results.append({
                    "idea_index": idx,
                    "idea_from_agent1": idea,
                    "data_collection": data_collection,
                    "markdown_path": data_collection.get('markdown_file_path'),
                    "status": "success"
                })
                
                if self.verbose:
                    print(f"   ✅ Data collected\n")
            
            except Exception as e:
                print(f"   ❌ Failed: {e}\n")
                agent2_results.append({
                    "idea_index": idx,
                    "idea_from_agent1": idea,
                    "status": "failed",
                    "error": str(e)
                })
        
        agent2_duration = (datetime.now() - agent2_start).total_seconds()
        
        # =========================================================================
        # STAGE 3: REPORT WRITING (Agent 3)
        # =========================================================================
        
        if self.verbose:
            print(f"\n{'─'*100}")
            print(f"STAGE 3: REPORT WRITING (Agent 3)")
            print(f"{'─'*100}\n")
        
        valid_for_reports = [r for r in agent2_results if r['status'] == 'success' and r.get('markdown_path')]
        reports_to_generate = valid_for_reports[:max_reports_to_generate]
        agent3_results = []
        agent3_start = datetime.now()
        
        for idx, data_output in enumerate(reports_to_generate):
            if self.verbose:
                print(f"\n   Generating Report {idx+1}/{len(reports_to_generate)}\n")
            
            try:
                report_result = await self.agent3.write_report(
                    agent2_markdown_path=data_output['markdown_path'],
                    idea_data=data_output['idea_from_agent1'],
                    output_format="both"
                )
                
                agent3_results.append({
                    "idea_index": idx,
                    "idea_from_agent1": data_output['idea_from_agent1'],
                    "report": report_result,
                    "pdf_path": report_result.get('pdf_path'),
                    "status": report_result.get('status', 'unknown')
                })
                
                if self.verbose:
                    print(f"   ✅ Report generated\n")
            
            except Exception as e:
                print(f"   ❌ Failed: {e}\n")
                agent3_results.append({
                    "idea_index": idx,
                    "status": "failed",
                    "error": str(e)
                })
        
        agent3_duration = (datetime.now() - agent3_start).total_seconds()
        
        # =========================================================================
        # STAGE 4: EMAIL DISTRIBUTION (Agent 4)
        # =========================================================================
        
        if send_email:
            if self.verbose:
                print(f"\n{'─'*100}")
                print(f"STAGE 4: EMAIL DISTRIBUTION (Agent 4)")
                print(f"{'─'*100}\n")
            
            valid_for_email = [r for r in agent3_results if r['status'] == 'success' and r.get('pdf_path')]
            agent4_results = []
            agent4_start = datetime.now()
            
            for idx, report_output in enumerate(valid_for_email):
                if self.verbose:
                    print(f"\n   Sending Email {idx+1}/{len(valid_for_email)}\n")
                
                try:
                    email_result = await self.agent4.send_report_email(
                        pdf_path=report_output['pdf_path'],
                        recipient_email=recipient_email,
                        idea_data=report_output['idea_from_agent1']
                    )
                    
                    agent4_results.append({
                        "idea_index": idx,
                        "email_result": email_result,
                        "status": email_result.get('status', 'unknown')
                    })
                    
                    if self.verbose and email_result.get('status') == 'success':
                        print(f"   ✅ Email sent successfully!\n")
                
                except Exception as e:
                    print(f"   ❌ Failed: {e}\n")
                    agent4_results.append({
                        "idea_index": idx,
                        "status": "failed",
                        "error": str(e)
                    })
            
            agent4_duration = (datetime.now() - agent4_start).total_seconds()
        else:
            agent4_results = []
            agent4_duration = 0
        
        # =========================================================================
        # PIPELINE COMPLETION
        # =========================================================================
        
        return self._create_result(
            "success", agent1_result, agent2_results, agent3_results, agent4_results,
            agent1_duration, agent2_duration, agent3_duration, agent4_duration, pipeline_start
        )
    
    def _create_result(self, status, agent1, agent2, agent3, agent4, 
                      t1, t2, t3, t4, start_time):
        """Create pipeline result dictionary."""
        pipeline_duration = (datetime.now() - start_time).total_seconds()
        
        result = {
            "status": status,
            "pipeline_metadata": {
                "execution_start": start_time.isoformat(),
                "execution_end": datetime.now().isoformat(),
                "total_duration_seconds": pipeline_duration
            },
            "agent1_result": agent1,
            "agent1_metadata": {
                "ideas_extracted": len(agent1.get('ideas_found', [])) if agent1 else 0,
                "duration_seconds": t1
            },
            "agent2_results": agent2,
            "agent2_metadata": {
                "ideas_researched": len(agent2),
                "successful_collections": len([r for r in agent2 if r.get('status') == 'success']),
                "duration_seconds": t2
            },
            "agent3_results": agent3,
            "agent3_metadata": {
                "reports_generated": len(agent3),
                "successful_reports": len([r for r in agent3 if r.get('status') == 'success']),
                "duration_seconds": t3
            },
            "agent4_results": agent4,
            "agent4_metadata": {
                "emails_sent": len(agent4),
                "successful_emails": len([r for r in agent4 if r.get('status') == 'success']),
                "duration_seconds": t4
            }
        }
        
        if self.verbose:
            print(f"\n{'='*100}")
            print(f"COMPLETE PIPELINE EXECUTION FINISHED (4 AGENTS)")
            print(f"{'='*100}")
            print(f"Total Duration: {pipeline_duration:.2f}s")
            print(f"Agent 1: {t1:.2f}s")
            print(f"Agent 2: {t2:.2f}s")
            print(f"Agent 3: {t3:.2f}s")
            print(f"Agent 4: {t4:.2f}s")
            print(f"Ideas Extracted: {result['agent1_metadata']['ideas_extracted']}")
            print(f"Data Collections: {result['agent2_metadata']['successful_collections']}")
            print(f"Reports Generated: {result['agent3_metadata']['successful_reports']}")
            print(f"Emails Sent: {result['agent4_metadata']['successful_emails']}")
            print(f"{'='*100}\n")
        
        return result
    
    def _create_error_result(self, status, error, agent_start, pipeline_start):
        """Create error result."""
        return {
            "status": status,
            "error": error,
            "pipeline_metadata": {
                "execution_start": pipeline_start.isoformat(),
                "total_duration_seconds": (datetime.now() - pipeline_start).total_seconds()
            }
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def run_complete_pipeline(
    input_text: str,
    source: str = "unknown",
    recipient: str = "mailsinghritivik@gmail.com",
    send_email: bool = True
) -> Dict:
    """
    Convenience function to run complete 4-agent pipeline.
    
    Args:
        input_text (str): Input text
        source (str): Source type
        recipient (str): Email recipient
        send_email (bool): Whether to send email
        
    Returns:
        Dict: Pipeline results
    """
    pipeline = CompleteInvestmentPipeline(verbose=True)
    return await pipeline.process_input(
        input_text=input_text,
        source=source,
        recipient_email=recipient,
        max_ideas_to_research=1,
        max_reports_to_generate=1,
        send_email=send_email
    )


# ============================================================================
# MAIN EXECUTION (FOR TESTING)
# ============================================================================

async def main():
    """Test the complete 4-agent pipeline."""
    
    test_input = """
Hey team, carbon credit marketplaces are exploding. Just saw Patch raise $55M.

The global carbon credit market is projected to grow from $838B in 2025 
to over $10 trillion by 2034.

Should we explore building a carbon credit marketplace platform? 
This could be a massive opportunity.
    """
    
    print("\n" + "="*100)
    print("COMPLETE 4-AGENT PIPELINE TEST")
    print("="*100 + "\n")
    
    pipeline = CompleteInvestmentPipeline(verbose=True)
    result = await pipeline.process_input(
        input_text=test_input,
        source="test_whatsapp",
        recipient_email="mailsinghritivik@gmail.com",
        max_ideas_to_research=1,
        max_reports_to_generate=1,
        send_email=True  # Will actually send email!
    )
    
    print("\n" + "="*100)
    print("PIPELINE RESULT SUMMARY")
    print("="*100)
    print(f"Status: {result['status']}")
    print(f"Total Duration: {result['pipeline_metadata']['total_duration_seconds']:.2f}s")
    print(f"Ideas Extracted: {result['agent1_metadata']['ideas_extracted']}")
    print(f"Reports Generated: {result['agent3_metadata']['reports_generated']}")
    print(f"Emails Sent: {result['agent4_metadata']['emails_sent']}")
    print("\n" + "="*100 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

