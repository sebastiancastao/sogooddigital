#!/usr/bin/env python3
"""
Test Script for AI Content Research Agent
Demonstrates the complete research-to-content pipeline
"""

import os
import sys
import logging
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_agent_initialization():
    """Test AI Content Research Agent initialization"""
    try:
        from ai_content_research_agent import AIContentResearchAgent, ContentSpecification
        
        # Initialize agent with fast testing mode (skip Google auth)
        agent = AIContentResearchAgent(skip_google_auth=True)
        
        # Get system status
        stats = agent.get_generation_statistics()
        
        logger.info("🎯 AI Content Research Agent Test")
        logger.info("=" * 50)
        logger.info(f"OpenAI Available: {stats['system_status']['openai_available']}")
        logger.info(f"Research Agent Available: {stats['system_status']['research_agent_available']}")
        logger.info(f"Document Creation Available: {stats['system_status']['document_creation_available']}")
        logger.info(f"Content Templates Loaded: {stats['content_templates_loaded']}")
        logger.info(f"Google Auth Skipped: {agent.skip_google_auth}")
        
        return agent, True
        
    except Exception as e:
        logger.error(f"❌ Agent initialization failed: {e}")
        return None, False

def test_content_specifications():
    """Test different content specification configurations"""
    try:
        from ai_content_research_agent import ContentSpecification
        
        # Test different content types
        content_types = [
            ("blog_post", "professional", "medium", "business_professionals"),
            ("article", "authoritative", "long", "academics"),
            ("social_media", "casual", "short", "general"),
            ("marketing_copy", "enthusiastic", "medium", "consumers"),
            ("whitepaper", "formal", "long", "executives")
        ]
        
        logger.info("\n📋 Testing Content Specifications")
        logger.info("-" * 30)
        
        for content_type, tone, length, audience in content_types:
            spec = ContentSpecification(
                content_type=content_type,
                content_tone=tone,
                content_length=length,
                target_audience=audience,
                additional_instructions=f"Test content for {content_type}"
            )
            
            logger.info(f"✅ {content_type}: {tone} tone, {length} length, {audience} audience")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Content specification test failed: {e}")
        return False

def test_keyword_extraction_fallback():
    """Test keyword extraction fallback functionality"""
    try:
        from ai_content_research_agent import AIContentResearchAgent
        
        agent = AIContentResearchAgent(skip_google_auth=True)
        
        # Test both fallback methods
        basic_keywords = agent._extract_keywords_fallback()
        enhanced_keywords = agent._extract_keywords_enhanced_fallback("test-doc-id")
        
        logger.info("\n🔑 Testing Keyword Extraction Fallback")
        logger.info("-" * 40)
        logger.info(f"Basic Fallback - Primary Keywords: {basic_keywords['primary_keywords']}")
        logger.info(f"Basic Fallback - Research Topics: {basic_keywords['research_topics']}")
        logger.info(f"Basic Fallback - Extraction Method: {basic_keywords['extraction_method']}")
        logger.info(f"Enhanced Fallback - Primary Keywords: {enhanced_keywords['primary_keywords'][:3]}")
        logger.info(f"Enhanced Fallback - Extraction Method: {enhanced_keywords['extraction_method']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Keyword extraction test failed: {e}")
        return False

def test_content_templates():
    """Test content template system"""
    try:
        from ai_content_research_agent import AIContentResearchAgent
        
        agent = AIContentResearchAgent(skip_google_auth=True)
        
        logger.info("\n📝 Testing Content Templates")
        logger.info("-" * 30)
        
        for content_type, template in agent.content_templates.items():
            logger.info(f"✅ {content_type.title()}: {len(template)} configuration items")
            
            # Show word ranges if available
            if 'word_ranges' in template:
                ranges = template['word_ranges']
                logger.info(f"   Word ranges: {ranges}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Content template test failed: {e}")
        return False

def test_prompt_generation():
    """Test content prompt generation"""
    try:
        from ai_content_research_agent import AIContentResearchAgent, ContentSpecification
        
        agent = AIContentResearchAgent(skip_google_auth=True)
        
        # Create test data
        keywords_data = {
            'primary_keywords': ['digital marketing', 'content strategy', 'AI technology'],
            'research_topics': ['marketing automation', 'customer engagement']
        }
        
        research_analysis = {
            'academic_analysis': {
                'marketing_summary': 'Test research analysis summary for digital marketing trends'
            },
            'marketing_analysis': {
                'executive_summary': 'Test marketing insights for business applications'
            },
            'papers_summary': [
                {
                    'title': 'AI in Digital Marketing',
                    'authors': ['Smith, J.', 'Johnson, A.'],
                    'citations': 150
                }
            ]
        }
        
        content_spec = ContentSpecification(
            content_type="blog_post",
            content_tone="professional",
            content_length="medium",
            target_audience="business_professionals",
            additional_instructions="Focus on practical implementation"
        )
        
        # Generate prompt
        prompt = agent._create_content_prompt(keywords_data, research_analysis, content_spec)
        
        logger.info("\n✨ Testing Prompt Generation")
        logger.info("-" * 30)
        logger.info(f"Prompt length: {len(prompt)} characters")
        logger.info(f"Contains keywords: {'digital marketing' in prompt}")
        logger.info(f"Contains specifications: {'blog_post' in prompt}")
        logger.info(f"Contains research data: {'AI in Digital Marketing' in prompt}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Prompt generation test failed: {e}")
        return False

def test_quality_calculation():
    """Test content quality calculation"""
    try:
        import re
        from ai_content_research_agent import AIContentResearchAgent, ContentSpecification
        
        agent = AIContentResearchAgent(skip_google_auth=True)
        
        # Test content
        test_content = """
# Digital Marketing Strategy

Digital marketing has revolutionized how businesses connect with customers. 
Modern approaches include social media engagement, content marketing, and data analytics.

## Key Benefits

- Improved customer targeting
- Real-time performance metrics
- Cost-effective reach
- Personalized experiences

## Implementation Steps

1. Define your target audience
2. Create compelling content
3. Choose appropriate channels
4. Monitor and optimize performance

This comprehensive approach ensures maximum impact for your marketing efforts.
        """.strip()
        
        content_spec = ContentSpecification(
            content_type="blog_post",
            content_length="medium"
        )
        
        research_analysis = {
            'papers_summary': [{'title': 'Test Paper'}] * 3
        }
        
        quality_score = agent._calculate_content_quality(test_content, content_spec, research_analysis)
        
        logger.info("\n⭐ Testing Quality Calculation")
        logger.info("-" * 30)
        logger.info(f"Test content length: {len(test_content.split())} words")
        logger.info(f"Quality score: {quality_score:.2f} ({quality_score*100:.1f}%)")
        logger.info(f"Has headings: {bool(re.search(r'#+\\s+', test_content))}")
        logger.info(f"Has lists: {bool(re.search(r'^\\s*[-*•]\\s+', test_content, re.MULTILINE))}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Quality calculation test failed: {e}")
        return False

def test_content_generation(agent):
    """Test actual content generation if OpenAI is available"""
    try:
        if not agent.client:
            logger.info("\n⚠️ OpenAI client not available - skipping content generation test")
            return True
        
        from ai_content_research_agent import ContentSpecification
        
        # Test data
        keywords_data = {
            'primary_keywords': ['artificial intelligence', 'business automation'],
            'research_topics': ['AI implementation', 'digital transformation']
        }
        
        research_analysis = {
            'academic_analysis': {
                'marketing_summary': 'AI is transforming business operations across industries'
            },
            'marketing_analysis': {
                'executive_summary': 'Businesses are adopting AI for competitive advantage'
            },
            'papers_summary': []
        }
        
        content_spec = ContentSpecification(
            content_type="blog_post",
            content_tone="professional",
            content_length="short",
            target_audience="business_professionals",
            additional_instructions="Keep it concise and actionable"
        )
        
        logger.info("\n🚀 Testing Content Generation")
        logger.info("-" * 30)
        logger.info("Generating content... (this may take 10-30 seconds)")
        
        # Generate content
        result = agent.generate_content(keywords_data, research_analysis, content_spec)
        
        logger.info(f"Generation successful: {result.generation_successful}")
        logger.info(f"Word count: {result.word_count}")
        logger.info(f"Generation time: {result.generation_time:.2f}s")
        logger.info(f"Quality score: {result.quality_score:.2f}")
        
        if result.generation_successful:
            logger.info(f"Content preview: {result.content[:200]}...")
        
        return result.generation_successful
        
    except Exception as e:
        logger.error(f"❌ Content generation test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    logger.info("🧪 Starting AI Content Research Agent Comprehensive Test")
    logger.info("=" * 60)
    
    tests = [
        ("Agent Initialization", test_agent_initialization),
        ("Content Specifications", test_content_specifications),
        ("Keyword Extraction Fallback", test_keyword_extraction_fallback),
        ("Content Templates", test_content_templates),
        ("Prompt Generation", test_prompt_generation),
        ("Quality Calculation", test_quality_calculation)
    ]
    
    passed = 0
    total = len(tests)
    agent = None
    
    for test_name, test_func in tests:
        logger.info(f"\n🔬 Running: {test_name}")
        
        if test_name == "Agent Initialization":
            agent, success = test_func()
        else:
            success = test_func()
        
        if success:
            passed += 1
            logger.info(f"✅ {test_name}: PASSED")
        else:
            logger.error(f"❌ {test_name}: FAILED")
    
    # Test content generation if agent is available
    if agent:
        logger.info(f"\n🔬 Running: Content Generation")
        if test_content_generation(agent):
            passed += 1
            total += 1
            logger.info("✅ Content Generation: PASSED")
        else:
            total += 1
            logger.error("❌ Content Generation: FAILED")
    
    # Final results
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! AI Content Research Agent is ready.")
        logger.info("\n📖 Usage Instructions:")
        logger.info("1. Set OPENAI_API_KEY environment variable")
        logger.info("2. Ensure google_scholar_research_agent.py is available")
        logger.info("3. Install dependencies: pip install openai python-docx")
        logger.info("4. Use agent.run_complete_content_pipeline() for full pipeline")
    else:
        logger.warning(f"⚠️ {total - passed} test(s) failed. Check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1) 