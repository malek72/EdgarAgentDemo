"""
Automated Single Complete 4-Agent Pipeline Test
Runs immediately without user confirmation
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
    """Run single complete 4-agent pipeline test automatically."""
    
    print("\n" + "="*100)
    print("COMPLETE 4-AGENT PIPELINE - AUTOMATED TEST")
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
    
    print("Running complete 4-agent pipeline...")
    print("Will send email to: mailtosinghritvik@gmail.com")
    print()
    
    test_start = datetime.now()
    
    # Initialize and run pipeline
    pipeline = CompleteInvestmentPipeline(verbose=True)
    
    result = await pipeline.process_input(
        input_text=test_input,
        source="email",
        recipient_email="mailtosinghritvik@gmail.com",
        max_ideas_to_research=1,
        max_reports_to_generate=1,
        send_email=True
    )
    
    test_duration = (datetime.now() - test_start).total_seconds()
    
    # Save result
    output_file = OUTPUT_DIR / f"complete_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump({
            "test_name": "complete_4agent_automated_test",
            "test_input": test_input,
            "pipeline_result": result,
            "test_duration": test_duration,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2, default=str)
    
    # Print summary
    print("\n" + "="*100)
    print("COMPLETE PIPELINE TEST - RESULTS")
    print("="*100)
    
    print(f"\nTotal Duration: {test_duration:.2f}s ({test_duration/60:.2f} minutes)")
    print(f"Status: {result.get('status', 'unknown')}")
    
    if result.get('status') == 'success':
        print(f"\n✅ Agent 1: {result['agent1_metadata']['ideas_extracted']} ideas extracted ({result['agent1_metadata']['duration_seconds']:.1f}s)")
        print(f"✅ Agent 2: {result['agent2_metadata']['successful_collections']} collections ({result['agent2_metadata']['duration_seconds']:.1f}s)")
        print(f"✅ Agent 3: {result['agent3_metadata']['successful_reports']} PDFs generated ({result['agent3_metadata']['duration_seconds']:.1f}s)")
        print(f"✅ Agent 4: {result['agent4_metadata']['successful_emails']} emails sent ({result['agent4_metadata']['duration_seconds']:.1f}s)")
        
        if result['agent4_results'] and result['agent4_results'][0].get('status') == 'success':
            email_id = result['agent4_results'][0]['email_result']['composio_result'][0]['data']['response_data']['id']
            print(f"\n📧 Email ID: {email_id}")
            print(f"📧 Recipient: mailtosinghritvik@gmail.com")
            print(f"📧 Status: SENT ✅")
    
    print(f"\n📁 Results saved to: {output_file}")
    print("\n" + "="*100 + "\n")
    
    return result


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

