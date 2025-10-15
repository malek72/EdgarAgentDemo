"""
Comprehensive Test Suite for Full Pipeline: Agent 1 → Agent 2

This test suite validates the complete multi-agent system:
- Agent 1: Idea Extraction
- Agent 2: Data Collection

All test outputs are saved to pipeline_test_outputs/ for manual validation.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
import nest_asyncio

from pipeline_agent1_agent2 import InvestmentPipeline

nest_asyncio.apply()

# Create output directory
OUTPUT_DIR = Path(__file__).parent / "pipeline_test_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================================
# TEST DATA - DIVERSE INPUTS
# ============================================================================

PIPELINE_TEST_INPUTS = {
    "email_explicit_startup": {
        "source": "email",
        "max_ideas": 1,  # Limit to 1 idea for deep research
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

Interested in taking a deeper look? They're giving us first right of refusal 
until Friday.

Regards,
Jennifer
        """
    },
    
    "whatsapp_carbon_marketplace": {
        "source": "whatsapp",
        "max_ideas": 1,
        "text": """
Dude check out this trend:

Carbon credit marketplaces are exploding - just saw Patch raise $55M

The global carbon credit market is projected to grow from $838B in 2025 
to over $10 trillion by 2034. Companies pursuing net-zero pledges, 
government policies, and ESG demands are driving this.

Should we explore building a carbon credit marketplace platform? 
Could be massive.
        """
    },
    
    "tweet_ai_agents": {
        "source": "twitter",
        "max_ideas": 1,
        "text": """
🚨 HOT TAKE: We're about to see a Cambrian explosion in AI agents. 

AutoGPT showed us it's possible. LangChain/LlamaIndex are building the 
infrastructure. Now we need the killer apps.

Mark my words: The first AI agent that can autonomously handle customer 
support end-to-end will be a unicorn within 18 months.

Market is ripe. Incumbents (Zendesk $17B, Intercom $1.3B) are too slow. 

Who's building this?
        """
    },
    
    "email_healthcare": {
        "source": "email",
        "max_ideas": 1,
        "text": """
Subject: Healthcare Tech Opportunity

Team,

My mom just got diagnosed with diabetes and the doctor gave her an ancient 
glucose monitor and a paper logbook. The apps don't integrate with insurance 
or share data with doctors automatically.

This is 2024! Why isn't this solved?

My research shows 37M Americans have diabetes, most are over 50 (not tech-savvy).
Medicare covers monitoring devices but they're all 20 years behind on UX.

Someone needs to build the "Apple Watch for chronic disease management" 
that actually works with insurance billing. This could be a $5B+ opportunity.

Thoughts?
- Mike
        """
    },
    
    "whatsapp_fintech": {
        "source": "whatsapp",
        "max_ideas": 1,
        "text": """
Did you see Bitcoin just crossed $45K? 📈

But real talk - the interesting play isn't crypto itself anymore, it's the 
infrastructure. Look at what Alchemy did (valued at $10B+). They're basically 
AWS for blockchain developers.

I'm hearing there's huge demand for:
- Wallet-as-a-service APIs
- NFT authentication tools for brands
- On-chain analytics platforms

Banks are finally getting serious about crypto custody too. That's a 
multi-billion dollar market waiting to happen.

The pick-and-shovel play > speculating on coins
        """
    },
}


# ============================================================================
# TEST EXECUTION FUNCTIONS
# ============================================================================

async def run_single_pipeline_test(
    pipeline: InvestmentPipeline,
    test_name: str,
    test_data: dict
) -> dict:
    """Run a single pipeline test and save output."""
    
    print(f"\n{'='*100}")
    print(f"RUNNING PIPELINE TEST: {test_name}")
    print(f"{'='*100}\n")
    
    test_start = datetime.now()
    
    try:
        result = await pipeline.process_input(
            input_text=test_data["text"],
            source=test_data["source"],
            max_ideas_to_research=test_data.get("max_ideas", 1)
        )
        
        test_duration = (datetime.now() - test_start).total_seconds()
        
        # Add test metadata
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
        json.dump(test_result, f, indent=2)
    
    print(f"\n✅ Pipeline test completed. Output saved to: {output_file}\n")
    
    return test_result


async def run_all_pipeline_tests():
    """Run all pipeline tests and generate summary report."""
    
    print(f"\n{'#'*100}")
    print(f"# FULL PIPELINE TEST SUITE: Agent 1 → Agent 2")
    print(f"# Total Tests: {len(PIPELINE_TEST_INPUTS)}")
    print(f"# Output Directory: {OUTPUT_DIR}")
    print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*100}\n")
    
    # Initialize pipeline
    pipeline = InvestmentPipeline(verbose=True)
    
    # Run all tests
    results = {}
    for test_name, test_data in PIPELINE_TEST_INPUTS.items():
        result = await run_single_pipeline_test(pipeline, test_name, test_data)
        results[test_name] = {
            "status": result["test_metadata"]["status"],
            "duration": result["test_metadata"]["test_duration"],
            "ideas_extracted": result["pipeline_result"]["agent1_metadata"]["ideas_extracted"] if result["pipeline_result"] else 0,
            "ideas_researched": result["pipeline_result"]["agent2_metadata"]["ideas_researched"] if result["pipeline_result"] else 0
        }
    
    # Generate summary report
    summary = generate_pipeline_summary(results)
    
    # Save summary
    summary_file = OUTPUT_DIR / f"pipeline_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print(f"\n{'#'*100}")
    print(f"# PIPELINE TEST SUITE COMPLETE")
    print(f"{'#'*100}\n")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Total Ideas Extracted: {summary['total_ideas_extracted']}")
    print(f"Total Ideas Researched: {summary['total_ideas_researched']}")
    print(f"Total Duration: {summary['total_duration']:.2f}s")
    print(f"\nSummary saved to: {summary_file}")
    print(f"\n{'#'*100}\n")
    
    return summary


def generate_pipeline_summary(results: dict) -> dict:
    """Generate a summary report of all pipeline test results."""
    
    total = len(results)
    passed = sum(1 for r in results.values() if r["status"] == "success")
    failed = total - passed
    total_ideas_extracted = sum(r.get("ideas_extracted", 0) for r in results.values())
    total_ideas_researched = sum(r.get("ideas_researched", 0) for r in results.values())
    total_duration = sum(r.get("duration", 0) for r in results.values())
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "success_rate": f"{(passed/total)*100:.1f}%",
        "total_ideas_extracted": total_ideas_extracted,
        "total_ideas_researched": total_ideas_researched,
        "avg_ideas_per_test": f"{total_ideas_extracted/total:.2f}" if total > 0 else "0",
        "total_duration": total_duration,
        "avg_duration_per_test": f"{total_duration/total:.2f}s" if total > 0 else "0s",
        "test_results": results
    }


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_pipeline_outputs():
    """Validate all pipeline test outputs against expected criteria."""
    
    print(f"\n{'='*100}")
    print("VALIDATING PIPELINE OUTPUTS")
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
        
        # Check 1: Agent 1 executed successfully
        validation["checks"]["agent1_executed"] = "agent1_result" in pipeline_result
        
        # Check 2: Ideas were extracted
        ideas_count = pipeline_result.get("agent1_metadata", {}).get("ideas_extracted", 0)
        validation["checks"]["ideas_extracted"] = ideas_count > 0
        validation["checks"]["ideas_count"] = ideas_count
        
        # Check 3: Agent 2 executed
        validation["checks"]["agent2_executed"] = len(pipeline_result.get("agent2_results", [])) > 0
        
        # Check 4: Data was collected
        if pipeline_result.get("agent2_results"):
            first_collection = pipeline_result["agent2_results"][0]
            validation["checks"]["data_collected"] = first_collection.get("status") == "success"
            
            if first_collection.get("data_collection"):
                dc = first_collection["data_collection"]
                validation["checks"]["has_data_collection"] = "data_collection" in dc or "raw_output" in dc
        
        # Check 5: Pipeline completed
        validation["checks"]["pipeline_completed"] = pipeline_result.get("status") == "success"
        
        # Overall pass/fail
        validation["overall_pass"] = all([
            validation["checks"].get("agent1_executed", False),
            validation["checks"].get("ideas_extracted", False),
            validation["checks"].get("agent2_executed", False),
            validation["checks"].get("pipeline_completed", False)
        ])
        
        validation_results.append(validation)
        
        status = "✅ PASS" if validation["overall_pass"] else "❌ FAIL"
        print(f"{status} - {test_data['test_name']}")
    
    # Save validation report
    validation_file = OUTPUT_DIR / f"pipeline_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    print("FULL PIPELINE TEST SUITE: Agent 1 → Agent 2")
    print("="*100)
    
    choice = input("""
Select test mode:
1. Run ALL pipeline tests (Agent 1 → Agent 2)
2. Run single test (choose which one)
3. Validate existing outputs
4. Quick test (first test case only)

Enter choice (1-4): """).strip()
    
    if choice == "1":
        await run_all_pipeline_tests()
        validate_pipeline_outputs()
    elif choice == "2":
        print("\nAvailable tests:")
        for idx, name in enumerate(PIPELINE_TEST_INPUTS.keys(), 1):
            print(f"{idx}. {name}")
        
        test_idx = int(input("\nEnter test number: ")) - 1
        test_name = list(PIPELINE_TEST_INPUTS.keys())[test_idx]
        test_data = PIPELINE_TEST_INPUTS[test_name]
        
        pipeline = InvestmentPipeline(verbose=True)
        await run_single_pipeline_test(pipeline, test_name, test_data)
    elif choice == "3":
        validate_pipeline_outputs()
    elif choice == "4":
        first_test = list(PIPELINE_TEST_INPUTS.items())[0]
        pipeline = InvestmentPipeline(verbose=True)
        await run_single_pipeline_test(pipeline, first_test[0], first_test[1])
    else:
        print("Invalid choice. Running all tests...")
        await run_all_pipeline_tests()
        validate_pipeline_outputs()


if __name__ == "__main__":
    asyncio.run(main())

