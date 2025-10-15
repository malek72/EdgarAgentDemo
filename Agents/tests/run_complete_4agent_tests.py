"""
Automated Test Runner for Complete 4-Agent Pipeline
Runs without user confirmation - for automated testing
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from test_complete_4agent_pipeline import run_all_complete_pipeline_tests
import nest_asyncio

nest_asyncio.apply()

async def main():
    """Run all 4-agent pipeline tests automatically."""
    
    print("\n" + "="*100)
    print("AUTOMATED COMPLETE 4-AGENT PIPELINE TEST SUITE")
    print("Agent 1 → Agent 2 → Agent 3 → Agent 4 (Email Distribution)")
    print("="*100 + "\n")
    
    print("⚠️  This will send real emails to mailsinghritivik@gmail.com\n")
    
    # Run all tests
    summary = await run_all_complete_pipeline_tests()
    
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
    print(f"Total Emails Sent: {summary['total_emails_sent']}")
    print(f"Total Duration: {summary['total_duration']:.2f}s")
    
    print("\n" + "="*100)
    print("✅ ALL 4-AGENT PIPELINE TESTS COMPLETE")
    print("="*100 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

