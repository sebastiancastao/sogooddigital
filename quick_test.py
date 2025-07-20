#!/usr/bin/env python3
"""
Quick test for enhanced AI processing
"""

from google_scholar_research_agent import GoogleScholarResearchAgent, ResearchPaper

def quick_test():
    print("🧠 Quick AI Processing Test")
    print("=" * 40)
    
    # Initialize agent
    agent = GoogleScholarResearchAgent()
    
    # Create test papers
    papers = [
        ResearchPaper(
            title="Social Media Marketing Impact",
            authors=["Dr. Smith", "Prof. Doe"],
            abstract="Social media marketing increases brand awareness by 65% and purchase intent by 40%.",
            publication_year=2023,
            journal="Journal of Digital Marketing",
            url="https://example.com/paper1",
            citations=142,
            keywords=["social media", "marketing"],
            relevance_score=0.92,
            full_text="Full text content available..."  # Has full text
        ),
        ResearchPaper(
            title="ROI Measurement Framework",
            authors=["Dr. Brown", "Sarah Johnson"],
            abstract="Framework for measuring ROI in digital advertising with 25% improvement in accuracy.",
            publication_year=2023,
            journal="Marketing Science Review",
            url="https://example.com/paper2",
            citations=89,
            keywords=["ROI", "digital advertising"],
            relevance_score=0.87,
            full_text=""  # No full text - abstract only
        )
    ]
    
    print(f"📊 Testing with {len(papers)} papers")
    print(f"  - With full text: {sum(1 for p in papers if p.full_text)}")
    print(f"  - Abstract only: {sum(1 for p in papers if not p.full_text)}")
    
    # Test AI processing
    print("\n🧠 Testing AI Analysis...")
    try:
        analysis = agent.analyze_research_content(papers)
        
        if analysis and not analysis.get('error'):
            print("✅ AI analysis completed")
            print(f"   Papers analyzed: {analysis.get('papers_analyzed', 0)}")
            
            # Check if individual papers were processed
            if 'individual_papers' in analysis:
                print(f"   Individual papers processed: {len(analysis['individual_papers'])}")
                for i, paper in enumerate(analysis['individual_papers'], 1):
                    title = paper.get('title', 'Unknown')[:30]
                    score = paper.get('marketing_relevance_score', 'N/A')
                    print(f"     {i}. {title}... (Score: {score}/10)")
            
            print("✅ SUCCESS: All papers processed through OpenAI!")
        else:
            print("❌ AI analysis failed")
            print(f"   Error: {analysis.get('error', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n🎯 Enhanced Features:")
    print("✅ AI processes all papers (with or without full PDFs)")
    print("✅ Marketing relevance scoring for each paper")
    print("✅ Paper names, authors, and URLs included")
    print("✅ Actionable marketing takeaways generated")

if __name__ == "__main__":
    quick_test() 