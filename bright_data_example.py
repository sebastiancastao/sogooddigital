"""
Example script demonstrating Bright Data API integration with Google Scholar Research Agent
"""

import os
from google_scholar_research_agent import GoogleScholarResearchAgent

def main():
    """
    Example of using Bright Data API for CAPTCHA bypass in Google Scholar research
    """
    
    print("🌐 Bright Data API Integration Example")
    print("=" * 50)
    
    # Set up environment variables (you need to set these)
    print("📋 Setting up environment variables...")
    
    # Required environment variables
    required_env_vars = [
        "OPENAI_API_KEY",
        "BRIGHT_DATA_API_KEY"  # Add your Bright Data API key here
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\nPlease set these environment variables:")
        print("export OPENAI_API_KEY='your_openai_api_key'")
        print("export BRIGHT_DATA_API_KEY='your_bright_data_api_key'")
        return
    
    print("✅ Environment variables configured")
    
    # Initialize the research agent
    print("\n🤖 Initializing Google Scholar Research Agent...")
    agent = GoogleScholarResearchAgent()
    
    # Configure Bright Data API
    print("\n🌐 Configuring Bright Data API...")
    agent.configure_bright_data_api(
        enable_bright_data=True,
        zone="web_unlocker1",  # Bright Data zone
        request_timeout=60,
        max_retries=3
    )
    
    # Configure enhanced CAPTCHA solver as backup
    print("🔧 Configuring enhanced CAPTCHA solver as backup...")
    agent.configure_enhanced_captcha_solver(
        enable_azcaptcha=True,
        prioritize_cost_effective=True,
        max_solve_attempts=3
    )
    
    # Example search queries
    search_queries = [
        "machine learning CAPTCHA bypass",
        "web scraping anti-bot detection",
        "automated research data extraction"
    ]
    
    print(f"\n🔍 Searching for papers with {len(search_queries)} queries...")
    print("This will use Bright Data API for CAPTCHA bypass when needed.")
    
    try:
        # Perform the search
        papers = agent.search_google_scholar(search_queries)
        
        print(f"\n📚 Search Results:")
        print(f"Found {len(papers)} papers total")
        
        # Display results
        for i, paper in enumerate(papers[:10], 1):  # Show first 10 papers
            print(f"\n{i}. {paper.title}")
            print(f"   Authors: {', '.join(paper.authors[:3])}{'...' if len(paper.authors) > 3 else ''}")
            print(f"   Year: {paper.publication_year}")
            print(f"   Citations: {paper.citations}")
            print(f"   Journal: {paper.journal}")
            if paper.abstract:
                print(f"   Abstract: {paper.abstract[:150]}...")
        
        # Get CAPTCHA solver statistics
        print("\n📊 CAPTCHA Solver Statistics:")
        stats = agent.get_captcha_solver_stats()
        if stats and not stats.get('error'):
            print(f"Enhanced solver stats: {stats}")
        
        # Show Bright Data usage if available
        if hasattr(agent, 'bright_data_enabled') and agent.bright_data_enabled:
            print("✅ Bright Data API was available and used for CAPTCHA bypass")
        else:
            print("❌ Bright Data API was not available")
            
    except Exception as e:
        print(f"❌ Error during search: {e}")
        print("This might be due to:")
        print("- Invalid API keys")
        print("- Network connectivity issues")
        print("- Service availability")
        
    finally:
        # Clean up resources
        print("\n🧹 Cleaning up resources...")
        agent.close_captcha_solver()
        print("✅ Cleanup complete")

if __name__ == "__main__":
    main() 