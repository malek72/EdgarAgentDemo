"""
Comprehensive Test Suite for Complete 4-Agent Pipeline

Agent 1: Idea Extractor
Agent 2: Data Collector (saves markdown)
Agent 3: Report Writer (generates PDF)
Agent 4: Mailing Agent (sends email)

All outputs saved to complete_pipeline_outputs/ for validation.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

import nest_asyncio
from Agents.core.pipeline_complete import CompleteInvestmentPipeline

nest_asyncio.apply()

# Create output directory
OUTPUT_DIR = Path(__file__).parent.parent / "test_outputs" / "complete_pipeline_tests"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================
# TEST DATA
# ============================================================================

COMPLETE_PIPELINE_TESTS = {
    "test1_carbon_marketplace_full": {
        "source": "whatsapp",
        "send_email": True,  # Will actually send email
        "text": """
Dude, carbon credit marketplaces are exploding! Just saw Patch raise $55M.

The global market is projected to grow from $838B in 2025 to over $10 trillion by 2034.

Should we build a carbon credit marketplace platform? Companies like Xpansiv (16.7% market share) 
and Verra are already dominating, but there's room for disruption with better tech.

This could be massive - thoughts?
        """
    },
    
    "test2_vertical_farming_full": {
        "source": "email",
        "send_email": True,
        "text": """
Subject: Investment Opportunity - UrbanFarm Robotics

Team,

UrbanFarm Robotics is building autonomous vertical farming systems for urban environments.

Metrics:
- $2M ARR, growing 400% YoY
- 15 pilot installations globally
- Unit economics: $150K per system, 60% gross margin
- Payback: 2.5 years

They're raising $5M Series A at $20M pre-money.

Vertical farming market: $12.77B by 2026 (26% CAGR).

Worth a deeper look?

Jennifer
        """
    }
}


# ============================================================================
# TEST EXECUTION
# ============================================================================

async def run_single_complete_pipeline_test(
    pipeline: CompleteInvestmentPipeline,
    test_name: str,
    test_data: dict
) -> dict:
    """Run single test through complete 4-agent pipeline."""
    
    print(f"\n{'='*100}")
    print(f"RUNNING COMPLETE PIPELINE TEST: {test_name}")
    print(f"{'='*100}\n")
    
    test_start = datetime.now()
    
    try:
        result = await pipeline.process_input(
            input_text=test_data["text"],
            source=test_data["source"],
            recipient_email="mailtosinghritvik@gmail.com",
            max_ideas_to_research=1,
            max_reports_to_generate=1,
            send_email=test_data.get("send_email", True)
        )
        
        test_duration = (datetime.now() - test_start).total_seconds()
        
        test_result = {
            "test_name": test_name,
            "test_input": test_data,
            "pipeline_result": result,
            "test_metadata": {
                "test_start": test_start.isoformat(),
                "test_duration": test_duration,
                "status": "success"
            }
        }
        
    except Exception as e:
        print(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        
        test_result = {
            "test_name": test_name,
            "test_input": test_data,
            "pipeline_result": None,
            "test_metadata": {
                "test_start": test_start.isoformat(),
                "test_duration": (datetime.now() - test_start).total_seconds(),
                "status": "failed",
                "error": str(e)
            }
        }
    
    # Save output
    output_file = OUTPUT_DIR / f"{test_name}.json"
    with open(output_file, "w") as f:
        json.dump(test_result, f, indent=2, default=str)
    
    print(f"\n✅ Test completed. Results saved to: {output_file}\n")
    
    return test_result


async def run_all_complete_pipeline_tests():
    """Run all 4-agent pipeline tests."""
    
    print(f"\n{'#'*100}")
    print(f"# COMPLETE 4-AGENT PIPELINE TEST SUITE")
    print(f"# Total Tests: {len(COMPLETE_PIPELINE_TESTS)}")
    print(f"# Output Directory: {OUTPUT_DIR}")
    print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*100}\n")
    
    # Initialize pipeline
    pipeline = CompleteInvestmentPipeline(verbose=True)
    
    # Run all tests
    results = {}
    for test_name, test_data in COMPLETE_PIPELINE_TESTS.items():
        result = await run_single_complete_pipeline_test(pipeline, test_name, test_data)
        
        if result["pipeline_result"]:
            pr = result["pipeline_result"]
            results[test_name] = {
                "status": result["test_metadata"]["status"],
                "duration": result["test_metadata"]["test_duration"],
                "ideas_extracted": pr.get("agent1_metadata", {}).get("ideas_extracted", 0),
                "reports_generated": pr.get("agent3_metadata", {}).get("successful_reports", 0),
                "emails_sent": pr.get("agent4_metadata", {}).get("successful_emails", 0)
            }
        else:
            results[test_name] = {
                "status": "failed",
                "error": result["test_metadata"].get("error", "Unknown")
            }
    
    # Generate summary
    summary = generate_complete_pipeline_summary(results)
    
    # Save summary
    summary_file = OUTPUT_DIR / f"complete_pipeline_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print(f"\n{'#'*100}")
    print(f"# COMPLETE 4-AGENT PIPELINE TEST SUITE FINISHED")
    print(f"{'#'*100}\n")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']}")
    print(f"Total Ideas: {summary['total_ideas_extracted']}")
    print(f"Total Reports: {summary['total_reports_generated']}")
    print(f"Total Emails: {summary['total_emails_sent']}")
    print(f"Total Duration: {summary['total_duration']:.2f}s")
    print(f"\nSummary saved to: {summary_file}")
    print(f"\n{'#'*100}\n")
    
    return summary


def generate_complete_pipeline_summary(results: dict) -> dict:
    """Generate summary of all 4-agent pipeline tests."""
    
    total = len(results)
    passed = sum(1 for r in results.values() if r.get("status") == "success")
    failed = total - passed
    total_ideas = sum(r.get("ideas_extracted", 0) for r in results.values())
    total_reports = sum(r.get("reports_generated", 0) for r in results.values())
    total_emails = sum(r.get("emails_sent", 0) for r in results.values())
    total_duration = sum(r.get("duration", 0) for r in results.values())
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "success_rate": f"{(passed/total)*100:.1f}%" if total > 0 else "0%",
        "total_ideas_extracted": total_ideas,
        "total_reports_generated": total_reports,
        "total_emails_sent": total_emails,
        "total_duration": total_duration,
        "avg_duration_per_test": f"{total_duration/total:.2f}s" if total > 0 else "0s",
        "test_results": results
    }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main test execution."""
    
    print("\n" + "="*100)
    print("COMPLETE 4-AGENT PIPELINE TEST SUITE")
    print("Agent 1 → Agent 2 → Agent 3 → Agent 4 (Email)")
    print("="*100)
    
    print("\n⚠️  WARNING: This will send real emails to mailtosinghritvik@gmail.com")
    confirm = input("Continue? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        print("\nTest cancelled.")
        return
    
    await run_all_complete_pipeline_tests()


if __name__ == "__main__":
    asyncio.run(main())

