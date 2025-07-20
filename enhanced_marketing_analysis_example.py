#!/usr/bin/env python3
"""
Enhanced Marketing Analysis Example
Demonstrates the enhanced Google Scholar Research Agent with OpenAI-powered marketing analysis
"""

import os
import json
import logging
from google_scholar_research_agent import GoogleScholarResearchAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to demonstrate enhanced marketing analysis"""
    
    print("🚀 Enhanced Marketing Analysis Example")
    print("=" * 60)
    
    # Initialize the research agent
    agent = GoogleScholarResearchAgent()
    
    # Configure Bright Data API for CAPTCHA bypass
    agent.configure_bright_data_api(
        enable_bright_data=True,
        api_key=os.getenv("BRIGHT_DATA_API_KEY", "your_api_key_here")  # Use your API key
    )
    
    # Configure PDF processing
    agent.configure_paper_download(
        enable_download=True,
        max_download_size_mb=50,
        download_timeout=30,
        max_parallel_downloads=3
    )
    
    # Define marketing research topics
    marketing_topics = [
        "consumer behavior digital marketing",
        "social media marketing effectiveness",
        "brand loyalty consumer psychology",
        "digital advertising ROI measurement"
    ]
    
    print(f"\n📊 Marketing Research Topics:")
    for i, topic in enumerate(marketing_topics, 1):
        print(f"  {i}. {topic}")
    
    # Step 1: Search Google Scholar for papers
    print(f"\n🔍 Step 1: Searching Google Scholar...")
    papers = agent.search_google_scholar(marketing_topics)
    
    if not papers:
        print("❌ No papers found! Check your Bright Data configuration.")
        return
    
    print(f"✅ Found {len(papers)} papers")
    
    # Step 2: Filter and rank papers
    print(f"\n🔬 Step 2: Filtering and ranking papers...")
    filtered_papers = agent.filter_and_rank_papers(papers, " ".join(marketing_topics))
    print(f"✅ Filtered to {len(filtered_papers)} relevant papers")
    
    # Step 3: Download and process PDFs
    print(f"\n📥 Step 3: Downloading and processing PDFs...")
    processed_papers = agent.download_and_process_pdfs(filtered_papers)
    pdfs_processed = len([p for p in processed_papers if p.full_text])
    print(f"✅ Processed {pdfs_processed} PDFs with full text")
    
    # Step 4: Enhanced research analysis with OpenAI
    print(f"\n🧠 Step 4: Enhanced research analysis with OpenAI...")
    analysis_data = agent.analyze_research_content(processed_papers)
    
    # Step 5: Enhanced marketing relevance analysis
    print(f"\n🎯 Step 5: Enhanced marketing relevance analysis...")
    keywords_data = {
        "primary_keywords": marketing_topics,
        "secondary_keywords": ["consumer behavior", "digital marketing", "brand strategy"],
        "research_topics": marketing_topics,
        "methodologies": ["quantitative analysis", "qualitative research", "case studies"]
    }
    
    marketing_analysis = agent.analyze_marketing_relevance(keywords_data, processed_papers)
    
    # Step 6: Create comprehensive document
    print(f"\n📄 Step 6: Creating comprehensive research document...")
    doc_filename = agent.create_research_document(
        analysis_data,
        f"Enhanced Marketing Analysis: {', '.join(marketing_topics)}",
        marketing_analysis
    )
    
    # Display results
    print(f"\n📋 Results Summary:")
    print("=" * 60)
    print(f"📄 Document Created: {doc_filename}")
    print(f"📊 Papers Found: {len(papers)}")
    print(f"🔍 Papers Analyzed: {len(processed_papers)}")
    print(f"📥 PDFs Processed: {pdfs_processed}")
    print(f"⭐ Average Relevance: {analysis_data.get('average_relevance', 0):.2f}/10")
    
    # Display individual paper analysis
    if 'individual_papers' in marketing_analysis:
        print(f"\n📝 Individual Paper Analysis:")
        print("-" * 40)
        
        for i, paper in enumerate(marketing_analysis['individual_papers'][:3], 1):  # Show first 3
            print(f"\n{i}. {paper.get('title', 'Unknown Title')}")
            print(f"   Authors: {', '.join(paper.get('authors', ['Unknown']))}")
            print(f"   Marketing Relevance: {paper.get('marketing_relevance_score', 'N/A')}/10")
            print(f"   URL: {paper.get('url', 'N/A')}")
            
            # Show marketing takeaways
            takeaways = paper.get('marketing_takeaways', [])
            if takeaways:
                print(f"   Marketing Takeaways:")
                for takeaway in takeaways[:2]:  # Show first 2
                    print(f"     • {takeaway}")
    
    # Display overall marketing insights
    if 'overall_marketing_analysis' in marketing_analysis:
        overall = marketing_analysis['overall_marketing_analysis']
        
        print(f"\n🎯 Overall Marketing Insights:")
        print("-" * 40)
        
        # Top trends
        trends = overall.get('top_marketing_trends', [])
        if trends:
            print(f"Top Marketing Trends:")
            for trend in trends[:3]:  # Show first 3
                print(f"  • {trend}")
        
        # Key recommendations
        recommendations = overall.get('marketing_strategy_recommendations', [])
        if recommendations:
            print(f"\nKey Recommendations:")
            for rec in recommendations[:3]:  # Show first 3
                print(f"  • {rec}")
    
    # Display quick actions
    if 'quick_actions' in marketing_analysis:
        print(f"\n⚡ Quick Actions for Marketing Teams:")
        print("-" * 40)
        for i, action in enumerate(marketing_analysis['quick_actions'], 1):
            print(f"  {i}. {action}")
    
    # Display Bright Data statistics
    bd_stats = agent.get_bright_data_stats()
    print(f"\n🌐 Bright Data Statistics:")
    print("-" * 40)
    print(f"  Requests Made: {bd_stats.get('requests_made', 0)}")
    print(f"  Success Rate: {bd_stats.get('success_rate', 0):.1f}%")
    print(f"  CAPTCHAs Bypassed: {bd_stats.get('captcha_bypassed', 0)}")
    print(f"  Avg Response Time: {bd_stats.get('average_response_time', 0):.2f}s")
    
    print(f"\n✅ Enhanced Marketing Analysis Complete!")
    print(f"📄 Check the document '{doc_filename}' for detailed analysis")
    print(f"🧠 Each paper was processed through OpenAI for marketing insights")
    print(f"📊 Marketing relevance scores and takeaways provided for each paper")

def show_paper_details(papers, limit=5):
    """Show detailed information about papers"""
    print(f"\n📋 Paper Details (showing first {limit}):")
    print("-" * 60)
    
    for i, paper in enumerate(papers[:limit], 1):
        print(f"\n{i}. {paper.title}")
        print(f"   Authors: {', '.join(paper.authors) if paper.authors else 'Unknown'}")
        print(f"   Year: {paper.publication_year}")
        print(f"   Journal: {paper.journal}")
        print(f"   Citations: {paper.citations}")
        print(f"   Relevance Score: {paper.relevance_score:.2f}/10")
        print(f"   URL: {paper.url}")
        if paper.abstract:
            print(f"   Abstract: {paper.abstract[:150]}...")
        if paper.full_text:
            print(f"   Full Text: Available ({len(paper.full_text)} chars)")
        else:
            print(f"   Full Text: Not available")

def demonstrate_openai_processing():
    """Demonstrate OpenAI processing capabilities"""
    print(f"\n🧠 OpenAI Processing Features:")
    print("-" * 40)
    print("✅ Paper summaries generated by OpenAI")
    print("✅ Marketing relevance scoring (1-10)")
    print("✅ Actionable marketing takeaways")
    print("✅ Business application recommendations")
    print("✅ Target industry identification")
    print("✅ Implementation strategies")
    print("✅ ROI potential assessment")
    print("✅ Consumer behavior insights")
    print("✅ Competitive advantage analysis")
    print("✅ Overall trend identification")
    print("✅ Executive summary generation")
    print("✅ Quick action recommendations")

if __name__ == "__main__":
    print("🎯 Enhanced Marketing Analysis with OpenAI Processing")
    print("=" * 60)
    
    # Show OpenAI features
    demonstrate_openai_processing()
    
    # Run the main example
    main() 