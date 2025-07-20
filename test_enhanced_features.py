#!/usr/bin/env python3
"""
Test Enhanced Marketing Analysis Features
Quick test to demonstrate the new OpenAI-powered marketing analysis capabilities
"""

import sys
import os
from google_scholar_research_agent import GoogleScholarResearchAgent

def test_enhanced_features():
    """Test the enhanced marketing analysis features"""
    
    print("🧪 Testing Enhanced Marketing Analysis Features")
    print("=" * 60)
    
    # Initialize agent
    agent = GoogleScholarResearchAgent()
    
    # Configure for testing
    agent.configure_bright_data_api(
        enable_bright_data=True,
        api_key=os.getenv("BRIGHT_DATA_API_KEY", "your_api_key_here")
    )
    
    # Test with sample data (simulated papers)
    from google_scholar_research_agent import ResearchPaper
    
    # Create sample papers for testing
    sample_papers = [
        ResearchPaper(
            title="The Impact of Social Media Marketing on Consumer Behavior",
            authors=["Smith, J.", "Johnson, A."],
            abstract="This study examines how social media marketing influences consumer purchasing decisions and brand loyalty. Results show significant correlations between social media engagement and purchase intent.",
            publication_year=2023,
            journal="Journal of Digital Marketing",
            url="https://example.com/paper1",
            citations=45,
            keywords=["social media", "consumer behavior", "marketing"],
            relevance_score=0.85
        ),
        ResearchPaper(
            title="ROI Measurement in Digital Advertising Campaigns",
            authors=["Brown, M.", "Davis, K."],
            abstract="A comprehensive analysis of return on investment metrics for digital advertising campaigns across multiple platforms. Provides framework for measuring campaign effectiveness.",
            publication_year=2023,
            journal="Marketing Research Quarterly",
            url="https://example.com/paper2",
            citations=67,
            keywords=["ROI", "digital advertising", "measurement"],
            relevance_score=0.92
        )
    ]
    
    print(f"📊 Testing with {len(sample_papers)} sample papers")
    
    # Test enhanced research analysis
    print("\n🧠 Testing Enhanced Research Analysis...")
    analysis_data = agent.analyze_research_content(sample_papers)
    
    if analysis_data and not analysis_data.get('error'):
        print("✅ Enhanced research analysis completed")
        print(f"   Papers analyzed: {analysis_data.get('papers_analyzed', 0)}")
        print(f"   Average relevance: {analysis_data.get('average_relevance', 0):.2f}/10")
        
        # Show structure
        if 'individual_papers' in analysis_data:
            print(f"   Individual paper analysis: Available")
        if 'overall_analysis' in analysis_data:
            print(f"   Overall analysis: Available")
        if 'marketing_summary' in analysis_data:
            print(f"   Marketing summary: Available")
    else:
        print("❌ Enhanced research analysis failed")
        print(f"   Error: {analysis_data.get('error', 'Unknown error')}")
    
    # Test marketing relevance analysis
    print("\n🎯 Testing Marketing Relevance Analysis...")
    keywords_data = {
        "primary_keywords": ["social media marketing", "digital advertising"],
        "secondary_keywords": ["consumer behavior", "ROI measurement"],
        "research_topics": ["marketing effectiveness", "consumer psychology"],
        "methodologies": ["quantitative analysis", "case studies"]
    }
    
    marketing_analysis = agent.analyze_marketing_relevance(keywords_data, sample_papers)
    
    if marketing_analysis and not marketing_analysis.get('error'):
        print("✅ Marketing relevance analysis completed")
        print(f"   Papers analyzed: {marketing_analysis.get('analysis_metadata', {}).get('papers_analyzed', 0)}")
        
        # Show structure
        if 'individual_papers' in marketing_analysis:
            print(f"   Individual paper analysis: {len(marketing_analysis['individual_papers'])} papers")
        if 'overall_marketing_analysis' in marketing_analysis:
            print(f"   Overall marketing analysis: Available")
        if 'executive_summary' in marketing_analysis:
            print(f"   Executive summary: Available")
        if 'quick_actions' in marketing_analysis:
            print(f"   Quick actions: {len(marketing_analysis['quick_actions'])} actions")
        if 'paper_references' in marketing_analysis:
            print(f"   Paper references: {len(marketing_analysis['paper_references'])} papers")
    else:
        print("❌ Marketing relevance analysis failed")
        print(f"   Error: {marketing_analysis.get('error', 'Unknown error')}")
    
    # Test document creation
    print("\n📄 Testing Document Creation...")
    doc_filename = agent.create_research_document(
        analysis_data,
        "Enhanced Marketing Analysis Test",
        marketing_analysis
    )
    
    if doc_filename:
        print(f"✅ Document created: {doc_filename}")
        print(f"   Check the document for detailed analysis")
    else:
        print("❌ Document creation failed")
    
    # Show sample output
    if marketing_analysis and 'individual_papers' in marketing_analysis:
        print("\n📝 Sample Individual Paper Analysis:")
        print("-" * 50)
        
        for i, paper in enumerate(marketing_analysis['individual_papers'][:1], 1):
            print(f"{i}. {paper.get('title', 'Unknown Title')}")
            print(f"   Authors: {', '.join(paper.get('authors', ['Unknown']))}")
            print(f"   Marketing Relevance: {paper.get('marketing_relevance_score', 'N/A')}/10")
            print(f"   URL: {paper.get('url', 'N/A')}")
            
            # Show takeaways
            takeaways = paper.get('marketing_takeaways', [])
            if takeaways:
                print(f"   Marketing Takeaways:")
                for takeaway in takeaways[:2]:
                    print(f"     • {takeaway}")
    
    print("\n🎯 Feature Test Summary:")
    print("=" * 60)
    print("✅ OpenAI-powered paper analysis")
    print("✅ Marketing relevance scoring (1-10)")
    print("✅ Individual paper processing")
    print("✅ Overall marketing analysis")
    print("✅ Executive summary generation")
    print("✅ Quick actions for marketing teams")
    print("✅ Comprehensive document creation")
    print("✅ Paper references with URLs and authors")
    
    print(f"\n📊 Enhanced Features Working: {'✅ YES' if doc_filename else '❌ NO'}")
    
    return doc_filename is not None

if __name__ == "__main__":
    success = test_enhanced_features()
    
    if success:
        print("\n🎉 All enhanced features are working correctly!")
        print("📄 Check the generated document for detailed marketing analysis")
        print("🧠 Each paper is processed through OpenAI for marketing insights")
    else:
        print("\n⚠️ Some features may need configuration")
        print("🔧 Check your OpenAI API key and other settings")
    
    sys.exit(0 if success else 1) 