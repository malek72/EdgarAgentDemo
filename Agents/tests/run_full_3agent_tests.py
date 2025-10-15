"""
Automated Test Runner for Complete 3-Agent Pipeline
No user input required - runs all tests automatically
"""

import asyncio
from test_full_3agent_pipeline import run_all_full_pipeline_tests, validate_full_pipeline_outputs
import nest_asyncio

nest_asyncio.apply()

async def main():
    """Run all 3-agent pipeline tests automatically."""
    
    print("\n" + "="*100)
    print("AUTOMATED FULL 3-AGENT PIPELINE TEST SUITE")
    print("Agent 1 (Idea Extractor) → Agent 2 (Data Collector) → Agent 3 (Report Writer)")
    print("="*100 + "\n")
    
    # Run all tests
    summary = await run_all_full_pipeline_tests()
    
    # Validate
    print("\n" + "="*100)
    print("VALIDATING ALL OUTPUTS")
    print("="*100 + "\n")
    
    validation_results = validate_full_pipeline_outputs()
    
    # Final summary
    print("\n" + "="*100)
    print("FINAL TEST SUMMARY")
    print("="*100)
    print(f"\nTotal Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']}")
    print(f"Total Ideas Extracted: {summary['total_ideas_extracted']}")
    print(f"Total Reports Generated: {summary['total_reports_generated']}")
    print(f"Total Duration: {summary['total_duration']:.2f}s")
    print(f"Avg Duration: {summary['avg_duration_per_test']}")
    
    passed_validation = sum(1 for v in validation_results if v['overall_pass'])
    print(f"\nValidation: {passed_validation}/{len(validation_results)} tests passed")
    
    print("\n" + "="*100)
    print("✅ ALL 3-AGENT PIPELINE TESTS COMPLETE")
    print("="*100 + "\n")
    
    # List generated reports
    from pathlib import Path
    reports_dir = Path(__file__).parent / "agent3_reports"
    if reports_dir.exists():
        markdown_reports = list(reports_dir.glob("*.md"))
        pdf_reports = list(reports_dir.glob("*.pdf"))
        print(f"Generated Reports:")
        print(f"  Markdown reports: {len(markdown_reports)}")
        print(f"  PDF reports: {len(pdf_reports)}")
        print(f"  Location: {reports_dir}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

