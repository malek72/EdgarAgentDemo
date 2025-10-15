#!/bin/bash

# Create organized structure
mkdir -p core tests test_outputs/agent1_tests test_outputs/agent2_tests test_outputs/agent3_tests test_outputs/pipeline_tests docs

# Move agent core files
mv idea_extractor_agent.py core/
mv data_collector_agent.py core/
mv report_writer_agent.py core/
mv pipeline_agent1_agent2.py core/
mv pipeline_full.py core/

# Move test files
mv test_*.py tests/
mv run_*.py tests/
mv quick_*.py tests/

# Move test outputs
mv test_outputs/* test_outputs/agent1_tests/
rmdir test_outputs
mv pipeline_test_outputs/* test_outputs/pipeline_tests/ 2>/dev/null || true
rmdir pipeline_test_outputs 2>/dev/null || true
mv full_pipeline_outputs/* test_outputs/pipeline_tests/ 2>/dev/null || true
rmdir full_pipeline_outputs 2>/dev/null || true

# Move Agent 2 and Agent 3 outputs
mv agent2_data_collection_outputs test_outputs/agent2_tests/
mv agent3_reports test_outputs/agent3_tests/

# Move documentation
mv *.md docs/

# Clean up
rm -f *.log
rm -rf __pycache__

echo "✅ Structure organized successfully!"
