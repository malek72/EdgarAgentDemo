"""
Run all comprehensive tests automatically
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
import sys

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from test_idea_extractor import run_all_tests, validate_test_outputs
import nest_asyncio

nest_asyncio.apply()

async def main():
    print("\n" + "="*100)
    print("STARTING COMPREHENSIVE TEST SUITE")
    print("="*100 + "\n")
    
    # Run all tests
    summary = await run_all_tests()
    
    print("\n" + "="*100)
    print("RUNNING VALIDATION")
    print("="*100 + "\n")
    
    # Validate outputs
    validation_results = validate_test_outputs()
    
    print("\n" + "="*100)
    print("FINAL SUMMARY")
    print("="*100)
    print(f"\nTotal Tests Run: {summary['total_tests']}")
    print(f"Passed: {summary['passed']} ({summary['success_rate']})")
    print(f"Failed: {summary['failed']}")
    print(f"Total Ideas Extracted: {summary['total_ideas_extracted']}")
    print(f"Average Ideas Per Test: {summary['avg_ideas_per_test']}")
    
    passed_validation = sum(1 for v in validation_results if v['overall_pass'])
    print(f"\nValidation Results:")
    print(f"  Tests Passed Validation: {passed_validation}/{len(validation_results)}")
    
    print("\n" + "="*100)
    print("✅ ALL TESTS COMPLETE - Check test_outputs/ folder for detailed results")
    print("="*100 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()

