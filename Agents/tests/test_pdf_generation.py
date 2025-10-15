"""Quick test to verify PDF generation with charts works"""

import asyncio
from pathlib import Path
import nest_asyncio
from report_writer_agent import ReportWriterAgent

nest_asyncio.apply()

async def main():
    print("Testing PDF generation with financial charts...\n")
    
    # Use existing markdown file from Agent 2
    agent2_dir = Path("agent2_data_collection_outputs")
    markdown_files = list(agent2_dir.glob("*.md"))
    
    if not markdown_files:
        print("No Agent 2 markdown files found. Run Agent 2 tests first.")
        return
    
    # Use first markdown file
    test_file = markdown_files[0]
    print(f"Using: {test_file}\n")
    
    # Create test idea data
    test_idea = {
        "idea": "Carbon Credit Marketplace Platform",
        "category": "business_opportunity",
        "market_sector": "Climate Tech",
        "validation": {"feasibility_score": "9/10"}
    }
    
    # Initialize Agent 3
    agent = ReportWriterAgent(verbose=True)
    
    # Generate report with PDF
    result = await agent.write_report(
        agent2_markdown_path=str(test_file),
        idea_data=test_idea,
        output_format="both"  # Generate both markdown and PDF
    )
    
    print("\n" + "="*80)
    print("RESULT:")
    print("="*80)
    print(f"Status: {result.get('status')}")
    print(f"Markdown: {result.get('markdown_path')}")
    print(f"PDF: {result.get('pdf_path')}")
    print(f"Word count: {result.get('word_count')}")
    
    if result.get('pdf_path'):
        pdf_path = Path(result['pdf_path'])
        if pdf_path.exists():
            pdf_size = pdf_path.stat().st_size
            print(f"\n✅ PDF generated successfully!")
            print(f"   Size: {pdf_size:,} bytes ({pdf_size/1024:.1f} KB)")
            print(f"   Location: {pdf_path}")
        else:
            print(f"\n❌ PDF file not found at: {pdf_path}")
    else:
        print(f"\n⚠️  PDF not generated (check errors above)")
    
    print("="*80)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

