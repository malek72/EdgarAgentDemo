"""
Agent 1: Idea Extractor Agent

This agent is the first step in a multi-agent investment pipeline. It:
1. Takes string input from emails, WhatsApp messages, or tweets
2. Uses Perplexity Sonar API with built-in web search capabilities
3. Extracts business or investment opportunities
4. Validates ideas through internet-based sources (Sonar auto-searches the web)
5. Outputs structured data for handoff to the data_collector agent

Architecture:
- Uses OpenAI Agents SDK with custom AsyncOpenAI client
- Configured for Perplexity Sonar API endpoint
- Leverages Sonar's built-in web search (no function tools needed)

Note: Perplexity Sonar models automatically search the web and provide
grounded responses with citations. No function tools required.
"""

import asyncio
import os
import json
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

# Import OpenAI async client
from openai import AsyncOpenAI

# Import agents framework components
from agents import Agent, OpenAIChatCompletionsModel, Runner, set_tracing_disabled

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
BASE_URL = os.getenv("EXAMPLE_BASE_URL") or "https://api.perplexity.ai"
API_KEY = os.getenv("EXAMPLE_API_KEY")
MODEL_NAME = os.getenv("EXAMPLE_MODEL_NAME") or "sonar-pro"

# Validate configuration
if not API_KEY:
    raise ValueError(
        "EXAMPLE_API_KEY not found. Please set it in your .env file."
    )

# Initialize the custom OpenAI async client for Perplexity
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)

# Disable tracing (optional, adjust for your needs)
set_tracing_disabled(disabled=True)


# ============================================================================
# IDEA EXTRACTOR AGENT CLASS
# ============================================================================

class IdeaExtractorAgent:
    """
    Agent 1: Extracts and validates business/investment ideas from text inputs.
    
    This agent processes unstructured text from various sources (emails, messages, 
    tweets) and extracts actionable business or investment opportunities with 
    validation from web sources.
    """
    
    def __init__(self, model_name: str = MODEL_NAME, verbose: bool = True):
        """
        Initialize the Idea Extractor Agent.
        
        Args:
            model_name (str): Perplexity model to use (default: sonar-pro)
            verbose (bool): Enable detailed logging
        """
        self.model_name = model_name
        self.verbose = verbose
        self.agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the agent with custom instructions."""
        
        instructions = """
        You are an expert investment analyst specializing in identifying business and investment opportunities.
        You have access to real-time web search through your Perplexity Sonar capabilities.
        
        Your PRIMARY TASK:
        1. Analyze the input text carefully
        2. Extract ANY business ideas, investment opportunities, market trends, or entrepreneurial concepts
        3. An "idea" can be:
           - A business opportunity mentioned explicitly
           - An emerging market trend that could be leveraged
           - A problem statement that suggests a business solution
           - Investment opportunities in companies, sectors, or assets
           - New technologies or products gaining traction
           - Market gaps or inefficiencies identified
        
        Your ANALYSIS PROCESS:
        1. READ the entire input text
        2. IDENTIFY all potential ideas (even subtle ones)
        3. For each idea found:
           - Use your web search capabilities to validate it
           - Check recent market developments and news
           - Find relevant metrics and data (market size, growth rates, funding)
           - Research competitors and similar solutions
           - Assess feasibility and market conditions
        4. CITE your sources with URLs when possible
        
        Your OUTPUT FORMAT (strict JSON):
        {
            "ideas_found": [
                {
                    "idea": "Clear description of the business/investment idea",
                    "source_context": "Relevant quote or context from the input",
                    "category": "business_opportunity|investment_opportunity|market_trend|technology|problem_solution",
                    "market_sector": "Industry or sector this relates to",
                    "validation": {
                        "market_viability": "Assessment based on web research",
                        "recent_developments": "Latest news/trends found with sources",
                        "key_metrics": "Relevant numbers and data points with sources",
                        "competitors": "Similar companies or solutions found",
                        "feasibility_score": "1-10 with detailed explanation"
                    },
                    "sources": ["URL1", "URL2", "..."],
                    "next_steps": "Recommended actions for data_collector agent"
                }
            ],
            "summary": "Overall assessment of ideas found",
            "confidence": "high|medium|low - your confidence in the extraction"
        }
        
        IMPORTANT RULES:
        - If NO clear idea is found, return {"ideas_found": [], "summary": "No business or investment ideas identified in the text.", "confidence": "high"}
        - Always search the web to validate findings before responding
        - Be thorough - check multiple angles before finalizing
        - Provide specific, actionable information with data
        - Include sources and citations (URLs) when possible
        - Focus on ACTIONABLE opportunities, not just general observations
        - Return ONLY valid JSON, no markdown formatting
        
        Be precise, data-driven, and comprehensive in your analysis.
        """
        
        self.agent = Agent(
            name="IdeaExtractorAgent",
            instructions=instructions,
            model=OpenAIChatCompletionsModel(
                model=self.model_name, 
                openai_client=client
            )
        )
    
    async def extract_ideas(self, input_text: str, source: str = "unknown") -> Dict:
        """
        Extract and validate business ideas from input text.
        
        Args:
            input_text (str): The text to analyze (from email, WhatsApp, tweet, etc.)
            source (str): Source of the input for logging purposes
            
        Returns:
            Dict: Structured output containing extracted ideas and validation
        """
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"[IdeaExtractorAgent] Processing input from: {source}")
            print(f"[IdeaExtractorAgent] Input length: {len(input_text)} characters")
            print(f"{'='*80}\n")
        
        try:
            # Enhance the query with context
            enhanced_query = f"""
            Analyze the following text and extract business or investment ideas.
            
            Source: {source}
            
            Text to analyze:
            ---
            {input_text}
            ---
            
            Please identify and validate any business or investment opportunities in this text.
            """
            
            # Run the agent
            result = await Runner.run(self.agent, enhanced_query)
            
            if self.verbose:
                print(f"\n[IdeaExtractorAgent] Analysis complete")
                print(f"[IdeaExtractorAgent] Response length: {len(result.final_output)} characters\n")
            
            # Parse the output
            output_data = self._parse_output(result.final_output, source)
            
            return output_data
            
        except Exception as e:
            print(f"[ERROR] IdeaExtractorAgent failed: {e}")
            return {
                "ideas_found": [],
                "summary": f"Error during extraction: {str(e)}",
                "confidence": "low",
                "metadata": {
                    "source": source,
                    "timestamp": datetime.now().isoformat(),
                    "status": "error",
                    "error": str(e)
                }
            }
    
    def _parse_output(self, output: str, source: str) -> Dict:
        """
        Parse the agent's output into structured format.
        
        Args:
            output (str): Raw output from the agent
            source (str): Source identifier
            
        Returns:
            Dict: Structured output with metadata
        """
        # Try to parse as JSON
        try:
            # Look for JSON in the output
            if "{" in output and "}" in output:
                start = output.find("{")
                end = output.rfind("}") + 1
                json_str = output[start:end]
                parsed = json.loads(json_str)
                
                # Add metadata
                parsed["metadata"] = {
                    "source": source,
                    "timestamp": datetime.now().isoformat(),
                    "model": self.model_name,
                    "status": "success"
                }
                
                return parsed
        except json.JSONDecodeError:
            pass
        
        # Fallback: return raw output with structure
        return {
            "ideas_found": [],
            "summary": output,
            "confidence": "medium",
            "metadata": {
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "model": self.model_name,
                "status": "raw_output",
                "note": "Could not parse as JSON, returning raw output"
            },
            "raw_output": output
        }
    
    async def process_batch(self, inputs: list[Dict[str, str]]) -> list[Dict]:
        """
        Process multiple inputs in batch.
        
        Args:
            inputs (list): List of dicts with 'text' and 'source' keys
            
        Returns:
            list: List of extraction results
        """
        results = []
        for item in inputs:
            result = await self.extract_ideas(
                input_text=item.get("text", ""),
                source=item.get("source", "unknown")
            )
            results.append(result)
        return results


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def extract_idea_from_text(text: str, source: str = "unknown") -> Dict:
    """
    Convenience function to extract ideas from text.
    
    Args:
        text (str): Input text to analyze
        source (str): Source identifier
        
    Returns:
        Dict: Extraction results
    """
    agent = IdeaExtractorAgent()
    return await agent.extract_ideas(text, source)


# ============================================================================
# MAIN EXECUTION (FOR TESTING)
# ============================================================================

async def main():
    """
    Main function for testing the agent.
    """
    # Example test input
    test_input = """
    Hey, I've been noticing that sustainable packaging is becoming huge. 
    Companies like Boxed Water are doing really well. Maybe we should look 
    into biodegradable packaging solutions for e-commerce. The market is 
    projected to grow at 15% CAGR through 2028.
    """
    
    agent = IdeaExtractorAgent(verbose=True)
    result = await agent.extract_ideas(test_input, source="test_email")
    
    print("\n" + "="*80)
    print("FINAL OUTPUT:")
    print("="*80)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())

