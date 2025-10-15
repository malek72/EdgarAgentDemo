"""
Integrated Pipeline: Agent 1 → Agent 2

This module implements the complete pipeline from idea extraction to data collection.

Flow:
1. Agent 1 (Idea Extractor) receives string input from email/WhatsApp/tweet
2. Agent 1 extracts and validates business/investment ideas
3. For each idea, Agent 2 (Data Collector) performs deep research
4. Complete results saved for Agent 3 (Report Writer)

Architecture Decision: Uses result.final_output for explicit control and validation
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import nest_asyncio

from idea_extractor_agent import IdeaExtractorAgent
from data_collector_agent import DataCollectorAgent

nest_asyncio.apply()


# ============================================================================
# INTEGRATED PIPELINE CLASS
# ============================================================================

class InvestmentPipeline:
    """
    Complete pipeline orchestrating Agent 1 and Agent 2.
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the pipeline with both agents.
        
        Args:
            verbose (bool): Enable detailed logging
        """
        self.verbose = verbose
        self.agent1 = IdeaExtractorAgent(verbose=verbose)
        self.agent2 = DataCollectorAgent(verbose=verbose)
        
        if verbose:
            print("\n" + "="*100)
            print("INVESTMENT PIPELINE INITIALIZED")
            print("="*100)
            print("Agent 1: Idea Extractor - Ready ✅")
            print("Agent 2: Data Collector - Ready ✅")
            print("="*100 + "\n")
    
    async def process_input(
        self, 
        input_text: str, 
        source: str = "unknown",
        max_ideas_to_research: int = 3
    ) -> Dict:
        """
        Process input through the complete pipeline.
        
        Args:
            input_text (str): Raw input (email, WhatsApp, tweet)
            source (str): Source type
            max_ideas_to_research (int): Max ideas to send to Agent 2
            
        Returns:
            Dict: Complete pipeline results
        """
        pipeline_start = datetime.now()
        
        if self.verbose:
            print(f"\n{'='*100}")
            print(f"PIPELINE EXECUTION STARTED")
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
                "agent2_results": []
            }
        
        # Validate Agent 1 output
        ideas = agent1_result.get('ideas_found', [])
        confidence = agent1_result.get('confidence', 'low')
        
        if not ideas or confidence == 'low':
            if self.verbose:
                print(f"\n⚠️  No actionable ideas found or low confidence")
                print(f"   Stopping pipeline\n")
            
            return {
                "status": "no_actionable_ideas",
                "agent1_result": agent1_result,
                "agent2_results": [],
                "pipeline_duration": (datetime.now() - pipeline_start).total_seconds()
            }
        
        # =========================================================================
        # STAGE 2: DATA COLLECTION (Agent 2)
        # =========================================================================
        
        if self.verbose:
            print(f"\n{'─'*100}")
            print(f"STAGE 2: DATA COLLECTION (Agent 2)")
            print(f"{'─'*100}\n")
        
        # Limit ideas to research
        ideas_to_research = ideas[:max_ideas_to_research]
        
        if self.verbose and len(ideas) > max_ideas_to_research:
            print(f"   Note: Limiting to top {max_ideas_to_research} ideas (out of {len(ideas)} found)\n")
        
        agent2_results = []
        agent2_start = datetime.now()
        
        for idx, idea in enumerate(ideas_to_research):
            if self.verbose:
                print(f"\n   Researching Idea {idx+1}/{len(ideas_to_research)}:")
                print(f"   '{idea.get('idea', 'Unknown')[:80]}...'\n")
            
            try:
                data_collection = await self.agent2.collect_data(idea, source="agent1")
                agent2_results.append({
                    "idea_index": idx,
                    "idea_from_agent1": idea,
                    "data_collection": data_collection,
                    "status": "success"
                })
                
                if self.verbose:
                    sources_count = data_collection.get('sources_summary', {}).get('total_sources', 'Unknown')
                    print(f"   ✅ Data collection complete")
                    print(f"      Sources collected: {sources_count}\n")
                
            except Exception as e:
                print(f"   ❌ Data collection failed: {e}\n")
                agent2_results.append({
                    "idea_index": idx,
                    "idea_from_agent1": idea,
                    "data_collection": None,
                    "status": "failed",
                    "error": str(e)
                })
        
        agent2_duration = (datetime.now() - agent2_start).total_seconds()
        
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
            }
        }
        
        if self.verbose:
            print(f"\n{'='*100}")
            print(f"PIPELINE EXECUTION COMPLETE")
            print(f"{'='*100}")
            print(f"Total Duration: {pipeline_duration:.2f}s")
            print(f"Agent 1 Duration: {agent1_duration:.2f}s")
            print(f"Agent 2 Duration: {agent2_duration:.2f}s")
            print(f"Ideas Extracted: {len(ideas)}")
            print(f"Ideas Researched: {len(ideas_to_research)}")
            print(f"Successful Collections: {pipeline_result['agent2_metadata']['successful_collections']}")
            print(f"{'='*100}\n")
        
        return pipeline_result
    
    async def process_batch(self, inputs: List[Dict]) -> List[Dict]:
        """
        Process multiple inputs through the pipeline.
        
        Args:
            inputs (List[Dict]): List of inputs with 'text' and 'source' keys
            
        Returns:
            List[Dict]: List of pipeline results
        """
        results = []
        
        for idx, input_data in enumerate(inputs):
            if self.verbose:
                print(f"\n{'#'*100}")
                print(f"PROCESSING BATCH ITEM {idx+1}/{len(inputs)}")
                print(f"{'#'*100}\n")
            
            result = await self.process_input(
                input_text=input_data.get('text', ''),
                source=input_data.get('source', 'unknown'),
                max_ideas_to_research=input_data.get('max_ideas', 3)
            )
            
            results.append(result)
        
        return results


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def run_pipeline(input_text: str, source: str = "unknown") -> Dict:
    """
    Convenience function to run the complete pipeline.
    
    Args:
        input_text (str): Input text to process
        source (str): Source type
        
    Returns:
        Dict: Pipeline results
    """
    pipeline = InvestmentPipeline(verbose=True)
    return await pipeline.process_input(input_text, source)


# ============================================================================
# MAIN EXECUTION (FOR TESTING)
# ============================================================================

async def main():
    """
    Main function for testing the integrated pipeline.
    """
    # Test input
    test_input = """
    Hey team, I've been noticing that sustainable packaging is becoming huge. 
    Companies like Boxed Water are doing really well. Maybe we should look 
    into biodegradable packaging solutions for e-commerce. The market is 
    projected to grow at 15% CAGR through 2028.
    """
    
    print("\n" + "="*100)
    print("INTEGRATED PIPELINE TEST")
    print("="*100 + "\n")
    
    pipeline = InvestmentPipeline(verbose=True)
    result = await pipeline.process_input(test_input, source="test_email", max_ideas_to_research=1)
    
    print("\n" + "="*100)
    print("PIPELINE RESULT SUMMARY")
    print("="*100)
    print(f"Status: {result['status']}")
    print(f"Total Duration: {result['pipeline_metadata']['total_duration_seconds']:.2f}s")
    print(f"Ideas Extracted: {result['agent1_metadata']['ideas_extracted']}")
    print(f"Ideas Researched: {result['agent2_metadata']['ideas_researched']}")
    print("="*100 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

