"""Quick test to verify the agent works"""

import asyncio
import json
import nest_asyncio
from idea_extractor_agent import IdeaExtractorAgent

nest_asyncio.apply()

async def main():
    print("Starting quick test...")
    
    test_input = """
    Hey team, I've been noticing that sustainable packaging is becoming huge. 
    Companies like Boxed Water are doing really well. Maybe we should look 
    into biodegradable packaging solutions for e-commerce. The market is 
    projected to grow at 15% CAGR through 2028.
    """
    
    print(f"\nInput: {test_input[:100]}...")
    
    agent = IdeaExtractorAgent(verbose=True)
    print("\nAgent initialized. Running extraction...")
    
    result = await agent.extract_ideas(test_input, source="test_email")
    
    print("\n" + "="*80)
    print("RESULT:")
    print("="*80)
    print(json.dumps(result, indent=2))
    
    return result

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

