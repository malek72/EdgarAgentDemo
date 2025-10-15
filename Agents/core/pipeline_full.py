"""
Complete 3-Agent Investment Analysis Pipeline

Agent 1: Idea Extractor - Extract business/investment ideas from text
Agent 2: Data Collector - Collect comprehensive financial data
Agent 3: Report Writer - Generate professional analysis report with PDF

Flow: Input → Agent 1 → Agent 2 (markdown) → Agent 3 (PDF report)
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

nest_asyncio.apply()


# ============================================================================
# COMPLETE 3-AGENT PIPELINE
# ============================================================================

class FullInvestmentPipeline:
    """
    Complete 3-agent pipeline for investment analysis.
    
    Agent 1: Extract ideas from unstructured text
    Agent 2: Collect comprehensive financial data
    Agent 3: Write professional analysis report (markdown + PDF)
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the complete pipeline with all three agents.
        
        Args:
            verbose (bool): Enable detailed logging
        """
        self.verbose = verbose
        self.agent1 = IdeaExtractorAgent(verbose=verbose)
        self.agent2 = DataCollectorAgent(verbose=verbose)
        self.agent3 = ReportWriterAgent(verbose=verbose)
        
        if verbose:
            print("\n" + "="*100)
            print("FULL INVESTMENT ANALYSIS PIPELINE INITIALIZED")
            print("="*100)
            print("Agent 1: Idea Extractor - Ready ✅")
            print("Agent 2: Data Collector - Ready ✅")
            print("Agent 3: Report Writer - Ready ✅")
            print("="*100 + "\n")
    
    async def process_input(
        self,
        input_text: str,
        source: str = "unknown",
        max_ideas_to_research: int = 1,
        max_reports_to_generate: int = 1,
        output_format: str = "both"  # "markdown", "pdf", or "both"
    ) -> Dict:
        """
        Process input through complete 3-agent pipeline.
        
        Args:
            input_text (str): Raw input (email, WhatsApp, tweet)
            source (str): Source type
            max_ideas_to_research (int): Max ideas for Agent 2
            max_reports_to_generate (int): Max reports for Agent 3
            output_format (str): Report format ("markdown", "pdf", or "both")
            
        Returns:
            Dict: Complete pipeline results
        """
        pipeline_start = datetime.now()
        
        if self.verbose:
            print(f"\n{'='*100}")
            print(f"FULL PIPELINE EXECUTION STARTED (3 AGENTS)")
            print(f"{'='*100}")
            print(f"Source: {source}")
            print(f"Input length: {len(input_text)} characters")
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
            return {
                "status": "failed_at_agent1",
                "error": str(e),
                "agent1_result": None,
                "agent2_results": [],
                "agent3_results": []
            }
        
        # Validate Agent 1 output
        ideas = agent1_result.get('ideas_found', [])
        confidence = agent1_result.get('confidence', 'low')
        
        if not ideas or confidence == 'low':
            if self.verbose:
                print(f"\n⚠️  No actionable ideas found or low confidence - stopping pipeline\n")
            
            return {
                "status": "no_actionable_ideas",
                "agent1_result": agent1_result,
                "agent2_results": [],
                "agent3_results": [],
                "pipeline_duration": (datetime.now() - pipeline_start).total_seconds()
            }
        
        # =========================================================================
        # STAGE 2: DATA COLLECTION (Agent 2)
        # =========================================================================
        
        if self.verbose:
            print(f"\n{'─'*100}")
            print(f"STAGE 2: DATA COLLECTION (Agent 2)")
            print(f"{'─'*100}\n")
        
        ideas_to_research = ideas[:max_ideas_to_research]
        
        if self.verbose and len(ideas) > max_ideas_to_research:
            print(f"   Note: Limiting to top {max_ideas_to_research} idea(s) for deep research\n")
        
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
                    save_markdown=True  # Save markdown for Agent 3
                )
                
                agent2_results.append({
                    "idea_index": idx,
                    "idea_from_agent1": idea,
                    "data_collection": data_collection,
                    "markdown_path": data_collection.get('markdown_file_path'),
                    "status": "success"
                })
                
                if self.verbose:
                    markdown_path = data_collection.get('markdown_file_path', 'N/A')
                    print(f"   ✅ Data collection complete")
                    print(f"      Markdown saved: {markdown_path}\n")
            
            except Exception as e:
                print(f"   ❌ Data collection failed: {e}\n")
                agent2_results.append({
                    "idea_index": idx,
                    "idea_from_agent1": idea,
                    "data_collection": None,
                    "markdown_path": None,
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
        
        # Filter successful data collections with markdown files
        valid_for_reports = [r for r in agent2_results if r['status'] == 'success' and r['markdown_path']]
        reports_to_generate = valid_for_reports[:max_reports_to_generate]
        
        if self.verbose and len(valid_for_reports) > max_reports_to_generate:
            print(f"   Note: Limiting to top {max_reports_to_generate} report(s)\n")
        
        agent3_results = []
        agent3_start = datetime.now()
        
        for idx, data_output in enumerate(reports_to_generate):
            if self.verbose:
                print(f"\n   Generating Report {idx+1}/{len(reports_to_generate)}:")
                print(f"   For: '{data_output['idea_from_agent1'].get('idea', 'Unknown')[:80]}...'\n")
            
            try:
                report_result = await self.agent3.write_report(
                    agent2_markdown_path=data_output['markdown_path'],
                    idea_data=data_output['idea_from_agent1'],
                    output_format=output_format
                )
                
                agent3_results.append({
                    "idea_index": idx,
                    "idea_from_agent1": data_output['idea_from_agent1'],
                    "report": report_result,
                    "status": report_result.get('status', 'unknown')
                })
                
                if self.verbose and report_result.get('status') == 'success':
                    print(f"   ✅ Report generated")
                    print(f"      Markdown: {report_result.get('markdown_path', 'N/A')}")
                    if 'pdf_path' in report_result:
                        print(f"      PDF: {report_result.get('pdf_path', 'N/A')}")
                    print(f"      Word count: {report_result.get('word_count', 'N/A')}\n")
            
            except Exception as e:
                print(f"   ❌ Report generation failed: {e}\n")
                agent3_results.append({
                    "idea_index": idx,
                    "idea_from_agent1": data_output['idea_from_agent1'],
                    "report": None,
                    "status": "failed",
                    "error": str(e)
                })
        
        agent3_duration = (datetime.now() - agent3_start).total_seconds()
        
        # =========================================================================
        # PIPELINE COMPLETION
        # =========================================================================
        
        pipeline_duration = (datetime.now() - pipeline_start).total_seconds()
        
        pipeline_result = {
            "status": "success",
            "pipeline_metadata": {
                "execution_start": pipeline_start.isoformat(),
                "execution_end": datetime.now().isoformat(),
                "total_duration_seconds": pipeline_duration,
                "source_type": source,
                "input_length": len(input_text)
            },
            "agent1_result": agent1_result,
            "agent1_metadata": {
                "ideas_extracted": len(ideas),
                "confidence": confidence,
                "duration_seconds": agent1_duration
            },
            "agent2_results": agent2_results,
            "agent2_metadata": {
                "ideas_researched": len(ideas_to_research),
                "successful_collections": len([r for r in agent2_results if r['status'] == 'success']),
                "failed_collections": len([r for r in agent2_results if r['status'] == 'failed']),
                "duration_seconds": agent2_duration
            },
            "agent3_results": agent3_results,
            "agent3_metadata": {
                "reports_generated": len(reports_to_generate),
                "successful_reports": len([r for r in agent3_results if r['status'] == 'success']),
                "failed_reports": len([r for r in agent3_results if r['status'] == 'failed']),
                "duration_seconds": agent3_duration
            }
        }
        
        if self.verbose:
            print(f"\n{'='*100}")
            print(f"FULL PIPELINE EXECUTION COMPLETE (3 AGENTS)")
            print(f"{'='*100}")
            print(f"Total Duration: {pipeline_duration:.2f}s")
            print(f"Agent 1 Duration: {agent1_duration:.2f}s")
            print(f"Agent 2 Duration: {agent2_duration:.2f}s")
            print(f"Agent 3 Duration: {agent3_duration:.2f}s")
            print(f"Ideas Extracted: {len(ideas)}")
            print(f"Ideas Researched: {len(ideas_to_research)}")
            print(f"Reports Generated: {len(reports_to_generate)}")
            print(f"Success Rate: Agent 1: 100%, Agent 2: {len([r for r in agent2_results if r['status']=='success'])}/{len(agent2_results)}, Agent 3: {len([r for r in agent3_results if r['status']=='success'])}/{len(agent3_results)}")
            print(f"{'='*100}\n")
        
        return pipeline_result


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def run_full_pipeline(
    input_text: str,
    source: str = "unknown",
    max_ideas: int = 1,
    output_format: str = "both"
) -> Dict:
    """
    Convenience function to run the complete 3-agent pipeline.
    
    Args:
        input_text (str): Input text to process
        source (str): Source type
        max_ideas (int): Max ideas to research and report on
        output_format (str): Report format
        
    Returns:
        Dict: Complete pipeline results
    """
    pipeline = FullInvestmentPipeline(verbose=True)
    return await pipeline.process_input(
        input_text=input_text,
        source=source,
        max_ideas_to_research=max_ideas,
        max_reports_to_generate=max_ideas,
        output_format=output_format
    )


# ============================================================================
# MAIN EXECUTION (FOR TESTING)
# ============================================================================

async def main():
    """Test the complete 3-agent pipeline."""
    
    test_input = """
Hey team, carbon credit marketplaces are exploding. Just saw Patch raise $55M.

The global carbon credit market is projected to grow from $838B in 2025 
to over $10 trillion by 2034. Companies pursuing net-zero pledges, 
government policies, and ESG demands are driving this.

Should we explore building a carbon credit marketplace platform? 
Could be massive opportunity.
    """
    
    print("\n" + "="*100)
    print("FULL 3-AGENT PIPELINE TEST")
    print("="*100 + "\n")
    
    pipeline = FullInvestmentPipeline(verbose=True)
    result = await pipeline.process_input(
        input_text=test_input,
        source="test_whatsapp",
        max_ideas_to_research=1,
        max_reports_to_generate=1,
        output_format="both"
    )
    
    print("\n" + "="*100)
    print("PIPELINE RESULT SUMMARY")
    print("="*100)
    print(f"Status: {result['status']}")
    print(f"Total Duration: {result['pipeline_metadata']['total_duration_seconds']:.2f}s")
    print(f"Ideas Extracted: {result['agent1_metadata']['ideas_extracted']}")
    print(f"Ideas Researched: {result['agent2_metadata']['ideas_researched']}")
    print(f"Reports Generated: {result['agent3_metadata']['reports_generated']}")
    
    if result['agent3_results']:
        for idx, report in enumerate(result['agent3_results']):
            if report['status'] == 'success':
                print(f"\nReport {idx+1}:")
                print(f"  Markdown: {report['report'].get('markdown_path', 'N/A')}")
                print(f"  PDF: {report['report'].get('pdf_path', 'N/A')}")
                print(f"  Word Count: {report['report'].get('word_count', 'N/A')}")
    
    print("\n" + "="*100 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

