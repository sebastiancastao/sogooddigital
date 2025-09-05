#!/usr/bin/env python3
"""
Test script for the enhanced AI Content Research Agent with Sieco-Tech blog scraping
"""

import os
import sys
from ai_content_research_agent import AIContentResearchAgent

def test_blog_scraping():
    """Test the blog scraping functionality"""
    
    # Initialize the agent
    agent = AIContentResearchAgent(
        openai_api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
    )
    
    print("🔍 Testing So Good Digital blog scraping...")
    
    # Test blog scraping
    blog_posts = agent.scrape_sogooddigital_blogs()
    
    print(f"✅ Scraped {len(blog_posts)} blog posts:")
    for i, post in enumerate(blog_posts[:3], 1):  # Show first 3 posts
        print(f"\n{i}. {post['title']}")
        print(f"   URL: {post['url']}")
        print(f"   Excerpt: {post['excerpt'][:100]}...")
    
    return blog_posts

def test_internal_link_generation():
    """Test the internal link generation with OpenAI analysis"""
    
    # Initialize the agent
    agent = AIContentResearchAgent(
        openai_api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
    )
    
    print("\n🤖 Testing internal link generation...")
    
    # Sample content for testing
    sample_content = """
    Content marketing is revolutionizing how B2B companies connect with their target audiences. 
    These strategic content solutions provide measurable business value across the entire 
    buying journey, helping organizations build trust and establish thought leadership.
    
    The implementation of effective content marketing requires careful planning and consideration 
    of various strategic factors. Trust-based marketing ensures that content resonates with 
    prospects and positions your brand as a trusted problem-solver.
    
    Modern content marketing integrates seamlessly with sales enablement strategies, 
    providing comprehensive lead nurturing capabilities. This data-driven approach enables 
    organizations to make informed decisions about marketing investments and ROI.
    
    The future of B2B marketing lies in content strategies that offer unprecedented 
    visibility into customer journeys. These systems not only generate leads but 
    also provide predictive analytics for proactive customer engagement.
    """
    
    # Scrape blogs first
    blog_posts = agent.scrape_sogooddigital_blogs()
    
    if blog_posts:
        # Test internal link analysis
        suggestions = agent.analyze_blog_content_for_links(sample_content, blog_posts)
        
        print(f"✅ Generated {len(suggestions)} internal link suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"\n{i}. Anchor: '{suggestion['anchor_phrase']}'")
            print(f"   URL: {suggestion['url']}")
    else:
        print("❌ No blog posts available for link analysis")
    
    return suggestions

def test_full_content_generation():
    """Test the complete content generation with internal and external links"""
    
    # Initialize the agent
    agent = AIContentResearchAgent(
        openai_api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
    )
    
    print("\n📝 Testing full content generation with links...")
    
    # Mock keywords data
    keywords_data = {
        'primary_keywords': ['content marketing', 'B2B marketing', 'digital marketing'],
        'secondary_keywords': ['sales enablement', 'lead generation', 'marketing strategy'],
        'research_topics': ['content strategy', 'B2B marketing automation']
    }
    
    # Mock research analysis
    research_analysis = {
        'papers_summary': ['Research paper 1', 'Research paper 2'],
        'research_quality': 'high'
    }
    
    # Mock content specification
    from ai_content_research_agent import ContentSpecification
    content_spec = ContentSpecification(
        content_type='blog_post',
        content_tone='professional',
        content_length='medium',
        target_audience='facility managers',
        include_research=True,
        include_citations=True
    )
    
    # Generate content
    result = agent.generate_content(keywords_data, research_analysis, content_spec)
    
    if result.generation_successful:
        print("✅ Content generated successfully!")
        print(f"Word count: {result.word_count}")
        print(f"Quality score: {result.quality_score}")
        print("\nGenerated content with links:")
        print("-" * 50)
        print(result.content)
        print("-" * 50)
    else:
        print("❌ Content generation failed")
        print(f"Error: {result.content}")
    
    return result

def main():
    """Main test function"""
    
    print("🚀 Testing Enhanced AI Content Research Agent")
    print("=" * 60)
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Some features may not work.")
        print("   Set your API key: export OPENAI_API_KEY='your-key-here'")
        print()
    
    try:
        # Test 1: Blog scraping
        blog_posts = test_blog_scraping()
        
        # Test 2: Internal link generation (only if we have API key)
        if os.getenv("OPENAI_API_KEY"):
            suggestions = test_internal_link_generation()
            
            # Test 3: Full content generation
            result = test_full_content_generation()
        else:
            print("\n⏭️  Skipping OpenAI-dependent tests (no API key)")
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
