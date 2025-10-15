"""
Automated Pipeline Test Runner - No user input required
Runs all 5 comprehensive tests: Agent 1 → Agent 2
"""

import asyncio
import sys
from test_full_pipeline import run_all_pipeline_tests, validate_pipeline_outputs
import nest_asyncio

nest_asyncio.apply()

async def main():
    """Run all tests automatically."""
    print("\n" + "="*100)
    print("AUTOMATED FULL PIPELINE TEST SUITE")
    print("Running all 5 tests: Agent 1 → Agent 2")
    print("="*100 + "\n")
    
    # Run all tests
    summary = await run_all_pipeline_tests()
    
    # Validate outputs
    print("\n" + "="*100)
    print("VALIDATING ALL OUTPUTS")
    print("="*100 + "\n")
    
    validation_results = validate_pipeline_outputs()
    
    # Final summary
    print("\n" + "="*100)
    print("FINAL TEST SUMMARY")
    print("="*100)
    print(f"\nTotal Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']}")
    print(f"Total Ideas Extracted: {summary['total_ideas_extracted']}")
    print(f"Total Ideas Researched: {summary['total_ideas_researched']}")
    print(f"Total Duration: {summary['total_duration']:.2f}s")
    print(f"Avg Duration per Test: {summary['avg_duration_per_test']}")
    
    passed_validation = sum(1 for v in validation_results if v['overall_pass'])
    print(f"\nValidation: {passed_validation}/{len(validation_results)} tests passed")
    
    print("\n" + "="*100)
    print("✅ ALL TESTS COMPLETE")
    print("="*100 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

