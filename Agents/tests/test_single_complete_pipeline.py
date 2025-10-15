"""
Single Complete 4-Agent Pipeline Test

Runs ONE comprehensive test through all 4 agents and saves all outputs.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

import nest_asyncio
from pipeline_complete import CompleteInvestmentPipeline

nest_asyncio.apply()

# Create output directory
OUTPUT_DIR = Path(__file__).parent.parent / "test_outputs" / "complete_4agent_test"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def main():
    """Run single complete 4-agent pipeline test."""
    
    print("\n" + "="*100)
    print("COMPLETE 4-AGENT PIPELINE - SINGLE COMPREHENSIVE TEST")
    print("Agent 1 → Agent 2 → Agent 3 → Agent 4")
    print("="*100 + "\n")
    
    test_input = """
Subject: Hot Investment Opportunity - Carbon Credit Marketplace

Team,

I've been tracking the carbon credit space and it's absolutely exploding right now.

Key Data Points:
- Patch (carbon marketplace) just raised $55M Series B
- Global market projected to grow from $838B (2025) to over $10 TRILLION by 2034
- That's a 32% CAGR - insane growth!
- Major players: Xpansiv (16.7% share), Verra (14.2%), Climate Impact X (8.8%)
- Corporate net-zero pledges driving demand
- Regulatory tailwinds (EU ETS, CORSIA, etc.)

Should we seriously look at building a carbon credit marketplace platform? 
The technology barrier is lowering (blockchain, APIs), and there's clear whitespace 
for a player focused on APAC or specific verticals.

This could be a $500M+ opportunity if we execute well. Thoughts?

Best,
Sarah
    """
    
    print("Test Input Preview:")
    print("-" * 80)
    print(test_input[:200] + "...")
    print("-" * 80)
    print()
    
    print("⚠️  This will:")
    print("  • Extract investment ideas (Agent 1)")
    print("  • Collect comprehensive financial data (Agent 2)")
    print("  • Generate PDF report with charts (Agent 3)")
    print("  • Send email to mailtosinghritvik@gmail.com (Agent 4)")
    print()
    
    confirm = input("Proceed with complete test? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        print("\nTest cancelled.")
        return
    
    print("\n" + "="*100)
    print("STARTING COMPLETE 4-AGENT PIPELINE TEST")
    print("="*100 + "\n")
    
    test_start = datetime.now()
    
    # Initialize pipeline
    pipeline = CompleteInvestmentPipeline(verbose=True)
    
    # Run complete pipeline
    result = await pipeline.process_input(
        input_text=test_input,
        source="email",
        recipient_email="mailtosinghritvik@gmail.com",
        max_ideas_to_research=1,
        max_reports_to_generate=1,
        send_email=True  # Will send real email!
    )
    
    test_duration = (datetime.now() - test_start).total_seconds()
    
    # Save complete result
    output_file = OUTPUT_DIR / f"complete_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump({
            "test_name": "complete_4agent_pipeline_single_test",
            "test_input": test_input,
            "pipeline_result": result,
            "test_duration": test_duration,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2, default=str)
    
    # Print comprehensive summary
    print("\n" + "="*100)
    print("COMPLETE PIPELINE TEST - FINAL RESULTS")
    print("="*100)
    
    print(f"\nTest Duration: {test_duration:.2f} seconds ({test_duration/60:.2f} minutes)")
    print(f"\nStatus: {result.get('status', 'unknown')}")
    
    if result.get('status') == 'success':
        print(f"\nAgent 1 Results:")
        print(f"  • Ideas Extracted: {result['agent1_metadata']['ideas_extracted']}")
        print(f"  • Confidence: {result['agent1_result'].get('confidence', 'N/A')}")
        print(f"  • Duration: {result['agent1_metadata']['duration_seconds']:.2f}s")
        
        print(f"\nAgent 2 Results:")
        print(f"  • Ideas Researched: {result['agent2_metadata']['ideas_researched']}")
        print(f"  • Successful Collections: {result['agent2_metadata']['successful_collections']}")
        print(f"  • Duration: {result['agent2_metadata']['duration_seconds']:.2f}s")
        
        if result['agent2_results']:
            markdown_path = result['agent2_results'][0].get('markdown_path')
            if markdown_path:
                print(f"  • Data Collection Markdown: {Path(markdown_path).name}")
        
        print(f"\nAgent 3 Results:")
        print(f"  • Reports Generated: {result['agent3_metadata']['reports_generated']}")
        print(f"  • Successful Reports: {result['agent3_metadata']['successful_reports']}")
        print(f"  • Duration: {result['agent3_metadata']['duration_seconds']:.2f}s")
        
        if result['agent3_results']:
            agent3_first = result['agent3_results'][0]
            if agent3_first.get('status') == 'success':
                report = agent3_first['report']
                print(f"  • Report Markdown: {Path(report.get('markdown_path', 'N/A')).name}")
                print(f"  • Report PDF: {Path(report.get('pdf_path', 'N/A')).name}")
                print(f"  • Report Word Count: {report.get('word_count', 'N/A')}")
        
        print(f"\nAgent 4 Results:")
        print(f"  • Emails Attempted: {result['agent4_metadata']['emails_sent']}")
        print(f"  • Emails Sent Successfully: {result['agent4_metadata']['successful_emails']}")
        print(f"  • Duration: {result['agent4_metadata']['duration_seconds']:.2f}s")
        
        if result['agent4_results']:
            agent4_first = result['agent4_results'][0]
            if agent4_first.get('status') == 'success':
                email_res = agent4_first['email_result']
                print(f"  • Recipient: {email_res.get('recipient', 'N/A')}")
                print(f"  • Email ID: {email_res.get('composio_result', [{}])[0].get('data', {}).get('response_data', {}).get('id', 'N/A')}")
                print(f"  • Status: SENT ✅")
    
    print(f"\nTest Results Saved To: {output_file}")
    
    print("\n" + "="*100)
    print("✅ COMPLETE 4-AGENT PIPELINE TEST FINISHED")
    print("="*100 + "\n")
    
    print("All outputs saved in:")
    print(f"  • Test result: {output_file}")
    print(f"  • Agent 2 markdown: {OUTPUT_DIR.parent / 'agent2_tests'}")
    print(f"  • Agent 3 PDF: {OUTPUT_DIR.parent / 'agent3_tests'}")
    
    return result


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()

