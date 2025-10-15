"""
Comprehensive Test Suite for Idea Extractor Agent

This test suite validates Agent 1 with diverse realistic inputs from:
- Emails
- WhatsApp messages
- Tweets

All test outputs are saved to test_outputs/ for manual validation.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
import nest_asyncio

from idea_extractor_agent import IdeaExtractorAgent

# Apply nest_asyncio for running in Jupyter/existing event loop
nest_asyncio.apply()

# Create output directory
OUTPUT_DIR = Path(__file__).parent / "test_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)


# ============================================================================
# TEST DATA - DUMMY INPUTS
# ============================================================================

TEST_INPUTS = {
    "email_1_explicit_business_idea": {
        "source": "email",
        "text": """
Subject: Potential Investment Opportunity - AI Tutoring Platform

Hi Team,

I wanted to share an interesting opportunity I came across. There's a growing market 
for AI-powered tutoring platforms, especially in STEM subjects. Companies like Khan 
Academy and Duolingo are seeing massive growth, but there's still a gap in personalized 
1-on-1 AI tutoring for high school and college students.

The edtech market is projected to reach $404B by 2025, with AI tutoring being one of 
the fastest-growing segments (32% CAGR). I think we should explore building or 
investing in this space.

Key points:
- Market size: $10B+ in US alone for tutoring services
- Growing demand post-pandemic for online learning
- AI advancements (GPT-4, Claude) make personalized tutoring scalable
- Subscription model could generate $30-50/month per student

What do you think? Should we schedule a deeper dive?

Best,
Sarah
        """
    },
    
    "email_2_problem_statement": {
        "source": "email",
        "text": """
Re: Customer Feedback from Q3

Hey everyone,

Just compiled the Q3 customer surveys and one thing keeps coming up: 
our enterprise clients are struggling with data migration when switching 
to our platform. They're saying it takes 4-6 weeks and requires hiring 
external consultants.

This is costing them $50K-100K per migration and it's becoming a major 
friction point in our sales process. Three deals fell through last quarter 
specifically because of migration concerns.

Maybe there's an opportunity here to build an automated migration tool or 
service? I know companies like Segment and Fivetran have built entire 
businesses around data integration.

Just a thought - wanted to flag this pattern.

- Marcus
        """
    },
    
    "whatsapp_1_market_trend": {
        "source": "whatsapp",
        "text": """
Yo! Did you see the news about lab-grown meat getting FDA approval? 
This is huge! 🥩

Just read that Upside Foods and Good Meat can now sell in the US. 
The cultivated meat market could hit $25 billion by 2030. 

My friend works at a VC firm and they're going crazy for this space. 
Companies raising at insane valuations right now.

Should we look into this? Could be perfect timing 🚀
        """
    },
    
    "whatsapp_2_casual_mention": {
        "source": "whatsapp",
        "text": """
Coffee tomorrow? ☕

Btw I was talking to my neighbor yesterday - he runs a small construction 
company and he's been complaining about how hard it is to find reliable 
workers. He uses some old software from like 2010 to manage projects and 
scheduling. Said he'd pay good money for something modern that actually 
works on mobile.

Anyway, see you tomorrow at 10?
        """
    },
    
    "whatsapp_3_multiple_ideas": {
        "source": "whatsapp",
        "text": """
Dude check out these trends I'm seeing:

1. Carbon credit marketplaces are exploding - just saw Patch raise $55M
2. Nobody has solved the last-mile delivery problem for groceries profitably yet
3. My sister's a nurse and says hospital shift-scheduling is a nightmare - 
   they still use Excel spreadsheets! 🤦‍♂️

Each of these could be a multi-million dollar opportunity. We should 
brainstorm which one to go after.
        """
    },
    
    "tweet_1_tech_trend": {
        "source": "twitter",
        "text": """
🚨 HOT TAKE: We're about to see a Cambrian explosion in AI agents. 

AutoGPT showed us it's possible. LangChain/LlamaIndex are building the infrastructure. 
Now we need the killer apps.

Mark my words: The first AI agent that can autonomously handle customer support 
end-to-end will be a unicorn within 18 months.

Market is ripe. Incumbents (Zendesk, Intercom) are too slow. 

Who's building this?
        """
    },
    
    "tweet_2_regulatory_change": {
        "source": "twitter",
        "text": """
BREAKING: EU passes comprehensive AI regulation act. 

High-risk AI systems now need compliance audits. This creates a MASSIVE 
opportunity for AI governance/compliance tools.

Similar to how GDPR created a $2B+ market for privacy compliance software.

Smart money is already moving into this space 💰
        """
    },
    
    "tweet_3_market_gap": {
        "source": "twitter",
        "text": """
Why is there no "Figma for data visualization" yet?

Tableau: enterprise bloatware, $70/mo
PowerBI: Microsoft lock-in
Looker: got acquired, stagnating

Opportunity: Build modern, collaborative, web-first BI tool.
TAM: $10B+. Recent funding: mode.com ($200M), hex.tech ($52M)

This space is heating up 🔥
        """
    },
    
    "email_3_investment_opportunity": {
        "source": "email",
        "text": """
Subject: FYI - Interesting Deal Flow

Team,

Just got off a call with a company called "UrbanFarm Robotics". They're 
building autonomous vertical farming systems for urban environments.

Key metrics:
- $2M ARR, growing 400% YoY
- 15 pilot installations in NYC, Tokyo, Singapore
- Unit economics: $150K per system, 60% gross margin
- Payback period for customers: 2.5 years vs traditional farming

They're raising a $5M Series A at a $20M pre-money valuation.

The vertical farming market is expected to reach $12.77B by 2026 (CAGR 26%).
With food security concerns and urbanization trends, this could be huge.

Interested in taking a deeper look? They're giving us first right of refusal 
until Friday.

Regards,
Jennifer
        """
    },
    
    "email_4_no_clear_idea": {
        "source": "email",
        "text": """
Subject: Team Lunch Next Week

Hey everyone,

Just wanted to coordinate for team lunch next Tuesday. I was thinking we 
could try that new Italian place downtown - I heard their pasta is amazing!

Please reply with your availability. Thinking around 12:30pm?

Also reminder that the office will be closed on Friday for the holiday.

Thanks!
Mike
        """
    },
    
    "whatsapp_4_crypto": {
        "source": "whatsapp",
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
        """
    },
    
    "tweet_4_subtle_opportunity": {
        "source": "twitter",
        "text": """
Spent 6 hours yesterday trying to consolidate my tax documents from 5 
different investment platforms (Robinhood, Coinbase, Vanguard, etc.)

Each has different export formats. None talk to each other. My accountant 
charges $200/hr to sort through this mess.

There has to be a better way... 😩

#taxseason #fintech
        """
    },
    
    "email_5_competitive_analysis": {
        "source": "email",
        "text": """
Subject: Competitor Analysis - Q4 2024

Hi Team,

Completed the competitive analysis for the dev tools space. Some concerning 
trends:

Vercel just announced $150M Series D ($2.5B valuation) - they're expanding 
beyond Next.js into full-stack platform
Railway raised $30M - positioning as "Heroku for the modern era"
Render growing 300% YoY with developer-friendly pricing

The gap I'm seeing: None of these players focus specifically on AI/ML 
deployment. Everyone building AI apps still struggles with:
- GPU orchestration
- Model versioning
- Inference optimization
- Cost management

Companies are paying 10x more than they should for ML infrastructure.

Potential whitespace opportunity? MLOps is projected to be $4B market by 2025.

Thoughts?

- Alex
        """
    },
    
    "whatsapp_5_healthcare": {
        "source": "whatsapp",
        "text": """
My mom just got diagnosed with diabetes and the doctor gave her this ancient 
glucose monitor and a paper logbook 🙄

There are apps but they don't integrate with her insurance or share data with 
her doctor automatically. She has to manually enter everything!

This is 2024! Why isn't this solved?? 

My research shows 37M Americans have diabetes, most are over 50 (not tech-savvy).
Medicare covers monitoring devices but they're all 20 years behind on UX.

Someone needs to build the "Apple Watch for chronic disease management" 
that actually works with insurance billing.
        """
    },
    
    "tweet_5_b2b_saas": {
        "source": "twitter",
        "text": """
SaaS founders: What's your biggest pain point right now?

Top 3 responses:
1. "Optimizing trial-to-paid conversion" (38%)
2. "Reducing churn" (31%)  
3. "Sales outreach at scale" (24%)

Hmm. Sounds like there's room for better product-led growth tools...

Companies like Pendo ($1B valuation) and Amplitude ($4B IPO) prove there's 
huge demand for user analytics/engagement platforms.

But I haven't seen anyone crack the "all-in-one PLG stack" yet 🤔
        """
    }
}


# ============================================================================
# TEST EXECUTION FUNCTIONS
# ============================================================================

async def run_single_test(agent: IdeaExtractorAgent, test_name: str, test_data: dict) -> dict:
    """Run a single test case and save output."""
    print(f"\n{'='*100}")
    print(f"RUNNING TEST: {test_name}")
    print(f"{'='*100}")
    
    result = await agent.extract_ideas(
        input_text=test_data["text"],
        source=test_data["source"]
    )
    
    # Save output
    output_file = OUTPUT_DIR / f"{test_name}.json"
    with open(output_file, "w") as f:
        json.dump({
            "test_name": test_name,
            "input": test_data,
            "output": result,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"✅ Test completed. Output saved to: {output_file}")
    
    return result


async def run_all_tests():
    """Run all test cases and generate summary report."""
    print(f"\n{'#'*100}")
    print(f"# IDEA EXTRACTOR AGENT - COMPREHENSIVE TEST SUITE")
    print(f"# Total Tests: {len(TEST_INPUTS)}")
    print(f"# Output Directory: {OUTPUT_DIR}")
    print(f"# Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*100}\n")
    
    # Initialize agent
    agent = IdeaExtractorAgent(verbose=True)
    
    # Run all tests
    results = {}
    for test_name, test_data in TEST_INPUTS.items():
        try:
            result = await run_single_test(agent, test_name, test_data)
            results[test_name] = {
                "status": "success",
                "ideas_count": len(result.get("ideas_found", [])),
                "confidence": result.get("confidence", "unknown")
            }
        except Exception as e:
            print(f"❌ Test {test_name} failed with error: {e}")
            results[test_name] = {
                "status": "failed",
                "error": str(e)
            }
    
    # Generate summary report
    summary = generate_summary_report(results)
    
    # Save summary
    summary_file = OUTPUT_DIR / f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print(f"\n{'#'*100}")
    print(f"# TEST SUITE COMPLETE")
    print(f"{'#'*100}\n")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Ideas Extracted: {summary['total_ideas_extracted']}")
    print(f"\nSummary saved to: {summary_file}")
    print(f"\n{'#'*100}\n")
    
    return summary


def generate_summary_report(results: dict) -> dict:
    """Generate a summary report of all test results."""
    total = len(results)
    passed = sum(1 for r in results.values() if r["status"] == "success")
    failed = total - passed
    total_ideas = sum(r.get("ideas_count", 0) for r in results.values() if r["status"] == "success")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "success_rate": f"{(passed/total)*100:.1f}%",
        "total_ideas_extracted": total_ideas,
        "avg_ideas_per_test": f"{total_ideas/passed:.2f}" if passed > 0 else "0",
        "test_results": results
    }


# ============================================================================
# SPECIFIC TEST FUNCTIONS
# ============================================================================

async def test_explicit_ideas():
    """Test cases with explicit business ideas."""
    print("\n### Testing: Explicit Business Ideas ###\n")
    agent = IdeaExtractorAgent(verbose=True)
    
    tests = {k: v for k, v in TEST_INPUTS.items() if "explicit" in k or "investment" in k}
    for test_name, test_data in tests.items():
        await run_single_test(agent, test_name, test_data)


async def test_subtle_ideas():
    """Test cases with subtle or implied ideas."""
    print("\n### Testing: Subtle/Implied Ideas ###\n")
    agent = IdeaExtractorAgent(verbose=True)
    
    tests = {k: v for k, v in TEST_INPUTS.items() if "problem" in k or "subtle" in k or "casual" in k}
    for test_name, test_data in tests.items():
        await run_single_test(agent, test_name, test_data)


async def test_no_ideas():
    """Test cases with no business ideas."""
    print("\n### Testing: No Ideas (Should return empty) ###\n")
    agent = IdeaExtractorAgent(verbose=True)
    
    tests = {k: v for k, v in TEST_INPUTS.items() if "no_clear_idea" in k}
    for test_name, test_data in tests.items():
        await run_single_test(agent, test_name, test_data)


async def test_by_source():
    """Test cases grouped by source (email, whatsapp, twitter)."""
    sources = ["email", "whatsapp", "twitter"]
    agent = IdeaExtractorAgent(verbose=True)
    
    for source in sources:
        print(f"\n### Testing: {source.upper()} Sources ###\n")
        tests = {k: v for k, v in TEST_INPUTS.items() if v["source"] == source}
        for test_name, test_data in tests.items():
            await run_single_test(agent, test_name, test_data)


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_test_outputs():
    """Validate all test outputs against expected criteria."""
    print(f"\n{'='*100}")
    print("VALIDATING TEST OUTPUTS")
    print(f"{'='*100}\n")
    
    validation_results = []
    
    for output_file in OUTPUT_DIR.glob("*.json"):
        if "summary" in output_file.name:
            continue
            
        with open(output_file, "r") as f:
            test_data = json.load(f)
        
        validation = {
            "test_name": test_data["test_name"],
            "checks": {}
        }
        
        output = test_data["output"]
        
        # Check 1: Has required fields
        validation["checks"]["has_ideas_found_field"] = "ideas_found" in output
        validation["checks"]["has_summary_field"] = "summary" in output
        validation["checks"]["has_confidence_field"] = "confidence" in output
        validation["checks"]["has_metadata"] = "metadata" in output
        
        # Check 2: Ideas structure
        if "ideas_found" in output:
            ideas = output["ideas_found"]
            validation["checks"]["ideas_is_list"] = isinstance(ideas, list)
            validation["checks"]["ideas_count"] = len(ideas)
            
            if len(ideas) > 0:
                first_idea = ideas[0]
                validation["checks"]["idea_has_required_fields"] = all(
                    field in first_idea for field in ["idea", "category", "validation"]
                )
        
        # Check 3: Confidence level is valid
        valid_confidence = output.get("confidence") in ["high", "medium", "low"]
        validation["checks"]["valid_confidence_level"] = valid_confidence
        
        # Overall pass/fail
        validation["overall_pass"] = all([
            validation["checks"].get("has_ideas_found_field", False),
            validation["checks"].get("has_summary_field", False),
            validation["checks"].get("ideas_is_list", True)
        ])
        
        validation_results.append(validation)
        
        status = "✅ PASS" if validation["overall_pass"] else "❌ FAIL"
        print(f"{status} - {test_data['test_name']}")
    
    # Save validation report
    validation_file = OUTPUT_DIR / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    print("IDEA EXTRACTOR AGENT - COMPREHENSIVE TEST SUITE")
    print("="*100)
    
    choice = input("""
Select test mode:
1. Run ALL tests
2. Test explicit ideas only
3. Test subtle ideas only
4. Test by source (email, whatsapp, twitter)
5. Validate existing outputs
6. Quick test (single example)

Enter choice (1-6): """).strip()
    
    if choice == "1":
        await run_all_tests()
        validate_test_outputs()
    elif choice == "2":
        await test_explicit_ideas()
    elif choice == "3":
        await test_subtle_ideas()
    elif choice == "4":
        await test_by_source()
    elif choice == "5":
        validate_test_outputs()
    elif choice == "6":
        agent = IdeaExtractorAgent(verbose=True)
        await run_single_test(agent, "email_1_explicit_business_idea", TEST_INPUTS["email_1_explicit_business_idea"])
    else:
        print("Invalid choice. Running all tests...")
        await run_all_tests()
        validate_test_outputs()


if __name__ == "__main__":
    asyncio.run(main())

