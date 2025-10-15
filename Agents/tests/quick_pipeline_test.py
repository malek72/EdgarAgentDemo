"""Quick pipeline test to verify Agent 1 → Agent 2 integration"""

import asyncio
import json
import nest_asyncio
from pipeline_agent1_agent2 import InvestmentPipeline

nest_asyncio.apply()

async def main():
    print("Starting quick pipeline test...\n")
    
    test_input = """
Hey team, carbon credit marketplaces are exploding. Just saw Patch raise $55M.

The market is projected to grow from $838B in 2025 to over $10 trillion by 2034.

Should we look into this space?
    """
    
    print("="*80)
    print("QUICK PIPELINE TEST: Agent 1 → Agent 2")
    print("="*80)
    print(f"Input: {test_input[:100]}...\n")
    
    pipeline = InvestmentPipeline(verbose=True)
    
    print("Running pipeline with max_ideas=1 for deep research...\n")
    
    result = await pipeline.process_input(
        input_text=test_input,
        source="test_whatsapp",
        max_ideas_to_research=1
    )
    
    print("\n" + "="*80)
    print("PIPELINE RESULT SUMMARY")
    print("="*80)
    print(f"Status: {result['status']}")
    print(f"Ideas Extracted: {result['agent1_metadata']['ideas_extracted']}")
    print(f"Ideas Researched: {result['agent2_metadata']['ideas_researched']}")
    print(f"Agent 1 Duration: {result['agent1_metadata']['duration_seconds']:.2f}s")
    print(f"Agent 2 Duration: {result['agent2_metadata']['duration_seconds']:.2f}s")
    print(f"Total Duration: {result['pipeline_metadata']['total_duration_seconds']:.2f}s")
    
    if result['agent2_results']:
        first_result = result['agent2_results'][0]
        if first_result['status'] == 'success':
            dc = first_result['data_collection']
            sources = dc.get('sources_summary', {}).get('total_sources', 'Unknown')
            print(f"\nData Collection Status: ✅ SUCCESS")
            print(f"Sources Collected: {sources}")
            
            # Print first 500 chars of data collection
            print(f"\nData Collection Preview:")
            print("-"*80)
            dc_str = json.dumps(dc, indent=2)
            print(dc_str[:1000] + "\n... [truncated] ...")
        else:
            print(f"\nData Collection Status: ❌ FAILED")
            print(f"Error: {first_result.get('error', 'Unknown')}")
    
    print("\n" + "="*80)
    print("✅ Quick pipeline test complete!")
    print("="*80 + "\n")
    
    return result

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

