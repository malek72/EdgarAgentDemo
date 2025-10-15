"""
Comprehensive Test Suite for Complete 3-Agent Pipeline

Agent 1: Idea Extractor
Agent 2: Data Collector (saves markdown)
Agent 3: Report Writer (generates PDF)

All outputs saved to full_pipeline_outputs/ for validation.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import nest_asyncio

from pipeline_full import FullInvestmentPipeline

nest_asyncio.apply()

# Create output directory
OUTPUT_DIR = Path(__file__).parent / "full_pipeline_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================================
# TEST DATA
# ============================================================================

FULL_PIPELINE_TESTS = {
    "test1_carbon_marketplace": {
        "source": "whatsapp",
        "text": """
Dude check out this trend:

Carbon credit marketplaces are exploding - just saw Patch raise $55M

The global carbon credit market is projected to grow from $838B in 2025 
to over $10 trillion by 2034. Companies pursuing net-zero pledges, 
government policies, and ESG demands are driving this.

Should we explore building a carbon credit marketplace platform? 
Companies like Xpansiv, Verra, and Gold Standard are already in this space.
Could be massive.
        """
    },
    
    "test2_vertical_farming": {
        "source": "email",
        "text": """
Subject: Investment Opportunity - UrbanFarm Robotics

Team,

Just got off a call with UrbanFarm Robotics. They're building autonomous 
vertical farming systems for urban environments.

Key metrics:
- $2M ARR, growing 400% YoY
- 15 pilot installations in NYC, Tokyo, Singapore
- Unit economics: $150K per system, 60% gross margin
- Payback period for customers: 2.5 years

They're raising a $5M Series A at a $20M pre-money valuation.

The vertical farming market is expected to reach $12.77B by 2026 (CAGR 26%).
With food security concerns and urbanization trends, this could be huge.

Interested in taking a deeper look?

Jennifer
        """
    },
    
    "test3_ai_customer_support": {
        "source": "twitter",
        "text": """
🚨 HOT TAKE: We're about to see a Cambrian explosion in AI agents. 

AutoGPT showed us it's possible. LangChain/LlamaIndex are building the 
infrastructure. Now we need the killer apps.

The first AI agent that can autonomously handle customer support end-to-end 
will be a unicorn within 18 months.

Market is ripe. Incumbents (Zendesk $17B market cap, Intercom $1.3B valuation) 
are too slow to innovate.

Customer support software market: $12B in 2024, projected $32B by 2030 (18% CAGR)

Who's building this?
        """
    }
}


# ============================================================================
# TEST EXECUTION
# ============================================================================

async def run_single_full_pipeline_test(
    pipeline: FullInvestmentPipeline,
    test_name: str,
    test_data: dict
) -> dict:
    """Run single test through complete 3-agent pipeline."""
    
    print(f"\n{'='*100}")
    print(f"RUNNING FULL PIPELINE TEST: {test_name}")
    print(f"{'='*100}\n")
    
    test_start = datetime.now()
    
    try:
        result = await pipeline.process_input(
            input_text=test_data["text"],
            source=test_data["source"],
            max_ideas_to_research=1,
            max_reports_to_generate=1,
            output_format="both"
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
    
    # Save test result
    output_file = OUTPUT_DIR / f"{test_name}.json"
    with open(output_file, "w") as f:
        json.dump(test_result, f, indent=2)
    
    print(f"\n✅ Test completed. Results saved to: {output_file}\n")
    
    return test_result


async def run_all_full_pipeline_tests():
    """Run all 3-agent pipeline tests."""
    
    print(f"\n{'#'*100}")
    print(f"# FULL 3-AGENT PIPELINE TEST SUITE")
    print(f"# Total Tests: {len(FULL_PIPELINE_TESTS)}")
    print(f"# Output Directory: {OUTPUT_DIR}")
    print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*100}\n")
    
    # Initialize pipeline
    pipeline = FullInvestmentPipeline(verbose=True)
    
    # Run all tests
    results = {}
    for test_name, test_data in FULL_PIPELINE_TESTS.items():
        result = await run_single_full_pipeline_test(pipeline, test_name, test_data)
        
        results[test_name] = {
            "status": result["test_metadata"]["status"],
            "duration": result["test_metadata"]["test_duration"],
            "ideas_extracted": result["pipeline_result"]["agent1_metadata"]["ideas_extracted"] if result["pipeline_result"] else 0,
            "reports_generated": result["pipeline_result"]["agent3_metadata"]["reports_generated"] if result["pipeline_result"] else 0
        }
    
    # Generate summary
    summary = generate_full_pipeline_summary(results)
    
    # Save summary
    summary_file = OUTPUT_DIR / f"full_pipeline_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print(f"\n{'#'*100}")
    print(f"# FULL 3-AGENT PIPELINE TEST SUITE COMPLETE")
    print(f"{'#'*100}\n")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Success Rate: {summary['success_rate']}")
    print(f"Total Ideas Extracted: {summary['total_ideas_extracted']}")
    print(f"Total Reports Generated: {summary['total_reports_generated']}")
    print(f"Total Duration: {summary['total_duration']:.2f}s")
    print(f"Avg Duration per Test: {summary['avg_duration_per_test']}")
    print(f"\nSummary saved to: {summary_file}")
    print(f"\n{'#'*100}\n")
    
    return summary


def generate_full_pipeline_summary(results: dict) -> dict:
    """Generate summary of all 3-agent pipeline tests."""
    
    total = len(results)
    passed = sum(1 for r in results.values() if r["status"] == "success")
    failed = total - passed
    total_ideas = sum(r.get("ideas_extracted", 0) for r in results.values())
    total_reports = sum(r.get("reports_generated", 0) for r in results.values())
    total_duration = sum(r.get("duration", 0) for r in results.values())
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "success_rate": f"{(passed/total)*100:.1f}%" if total > 0 else "0%",
        "total_ideas_extracted": total_ideas,
        "total_reports_generated": total_reports,
        "total_duration": total_duration,
        "avg_duration_per_test": f"{total_duration/total:.2f}s" if total > 0 else "0s",
        "test_results": results
    }


# ============================================================================
# VALIDATION
# ============================================================================

def validate_full_pipeline_outputs():
    """Validate all 3-agent pipeline outputs."""
    
    print(f"\n{'='*100}")
    print("VALIDATING FULL PIPELINE OUTPUTS (3 AGENTS)")
    print(f"{'='*100}\n")
    
    validation_results = []
    
    for output_file in OUTPUT_DIR.glob("*.json"):
        if "summary" in output_file.name or "validation" in output_file.name:
            continue
        
        with open(output_file, "r") as f:
            test_data = json.load(f)
        
        validation = {
            "test_name": test_data["test_name"],
            "checks": {}
        }
        
        pipeline_result = test_data.get("pipeline_result")
        
        if not pipeline_result:
            validation["checks"]["has_pipeline_result"] = False
            validation["overall_pass"] = False
            validation_results.append(validation)
            continue
        
        # Check Agent 1
        validation["checks"]["agent1_executed"] = "agent1_result" in pipeline_result
        validation["checks"]["agent1_ideas"] = pipeline_result.get("agent1_metadata", {}).get("ideas_extracted", 0)
        
        # Check Agent 2
        validation["checks"]["agent2_executed"] = len(pipeline_result.get("agent2_results", [])) > 0
        
        if pipeline_result.get("agent2_results"):
            agent2_first = pipeline_result["agent2_results"][0]
            validation["checks"]["agent2_success"] = agent2_first.get("status") == "success"
            validation["checks"]["agent2_markdown"] = agent2_first.get("markdown_path") is not None
        
        # Check Agent 3
        validation["checks"]["agent3_executed"] = len(pipeline_result.get("agent3_results", [])) > 0
        
        if pipeline_result.get("agent3_results"):
            agent3_first = pipeline_result["agent3_results"][0]
            validation["checks"]["agent3_success"] = agent3_first.get("status") == "success"
            
            if agent3_first.get("report"):
                report = agent3_first["report"]
                validation["checks"]["report_markdown"] = "markdown_path" in report
                validation["checks"]["report_pdf"] = "pdf_path" in report
                validation["checks"]["report_word_count"] = report.get("word_count", 0)
        
        # Overall pass/fail
        validation["overall_pass"] = all([
            validation["checks"].get("agent1_executed", False),
            validation["checks"].get("agent1_ideas", 0) > 0,
            validation["checks"].get("agent2_executed", False),
            validation["checks"].get("agent3_executed", False)
        ])
        
        validation_results.append(validation)
        
        status = "✅ PASS" if validation["overall_pass"] else "❌ FAIL"
        print(f"{status} - {test_data['test_name']}")
        if validation["overall_pass"]:
            print(f"     Agent 1: {validation['checks'].get('agent1_ideas', 0)} ideas")
            print(f"     Agent 2: {'✅' if validation['checks'].get('agent2_success') else '❌'}")
            print(f"     Agent 3: {'✅' if validation['checks'].get('agent3_success') else '❌'}")
            print(f"     Report words: {validation['checks'].get('report_word_count', 'N/A')}")
    
    # Save validation report
    validation_file = OUTPUT_DIR / f"full_pipeline_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(validation_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(validation_results),
            "passed": sum(1 for v in validation_results if v["overall_pass"]),
            "validations": validation_results
        }, f, indent=2)
    
    print(f"\nValidation report saved to: {validation_file}")
    return validation_results


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main test execution."""
    
    print("\n" + "="*100)
    print("FULL 3-AGENT PIPELINE TEST SUITE")
    print("Agent 1 → Agent 2 → Agent 3")
    print("="*100)
    
    choice = input("""
Select test mode:
1. Run ALL 3-agent pipeline tests
2. Run single test
3. Validate existing outputs
4. Quick test (first test only)

Enter choice (1-4): """).strip()
    
    if choice == "1":
        await run_all_full_pipeline_tests()
        validate_full_pipeline_outputs()
    elif choice == "2":
        print("\nAvailable tests:")
        for idx, name in enumerate(FULL_PIPELINE_TESTS.keys(), 1):
            print(f"{idx}. {name}")
        
        test_idx = int(input("\nEnter test number: ")) - 1
        test_name = list(FULL_PIPELINE_TESTS.keys())[test_idx]
        test_data = FULL_PIPELINE_TESTS[test_name]
        
        pipeline = FullInvestmentPipeline(verbose=True)
        await run_single_full_pipeline_test(pipeline, test_name, test_data)
    elif choice == "3":
        validate_full_pipeline_outputs()
    elif choice == "4":
        first_test = list(FULL_PIPELINE_TESTS.items())[0]
        pipeline = FullInvestmentPipeline(verbose=True)
        await run_single_full_pipeline_test(pipeline, first_test[0], first_test[1])
    else:
        print("Invalid choice. Running all tests...")
        await run_all_full_pipeline_tests()
        validate_full_pipeline_outputs()


if __name__ == "__main__":
    asyncio.run(main())

