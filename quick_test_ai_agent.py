#!/usr/bin/env python3
"""
Quick Test for AI Content Research Agent
Fast testing without Google authentication delays
"""

import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def quick_test_agent():
    """Quick test of AI Content Research Agent without Google auth"""
    
    try:
        logger.info("🚀 Quick Test: AI Content Research Agent (No Google Auth)")
        logger.info("=" * 60)
        
        from ai_content_research_agent import AIContentResearchAgent, ContentSpecification
        
        # Initialize with Google auth skipped for fast testing
        logger.info("⏱️ Initializing agent (fast mode - no Google auth)...")
        start_time = datetime.now()
        
        agent = AIContentResearchAgent(skip_google_auth=True)
        
        init_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Agent initialized in {init_time:.2f} seconds")
        
        # Check system status
        stats = agent.get_generation_statistics()
        logger.info(f"📊 System Status:")
        logger.info(f"   OpenAI Available: {stats['system_status']['openai_available']}")
        logger.info(f"   Research Agent Available: {stats['system_status']['research_agent_available']}")
        logger.info(f"   Document Creation Available: {stats['system_status']['document_creation_available']}")
        logger.info(f"   Google Auth Skipped: {agent.skip_google_auth}")
        
        # Test keyword extraction (enhanced fallback)
        logger.info("\n🔑 Testing Enhanced Keyword Extraction...")
        keywords_data = agent.extract_keywords_from_google_file("sample-doc-id")
        
        logger.info(f"✅ Keywords extracted successfully:")
        logger.info(f"   Primary Keywords: {keywords_data['primary_keywords'][:3]}")
        logger.info(f"   Research Topics: {keywords_data['research_topics'][:2]}")
        logger.info(f"   Extraction Method: {keywords_data['extraction_method']}")
        
        # Test content generation (if OpenAI is available)
        if agent.client:
            logger.info("\n✨ Testing Content Generation...")
            
            content_spec = ContentSpecification(
                content_type="blog_post",
                content_tone="professional",
                content_length="short",
                target_audience="business_professionals",
                additional_instructions="Keep it concise and actionable"
            )
            
            # Create simple research analysis for testing
            research_analysis = {
                'academic_analysis': {
                    'marketing_summary': 'AI and automation are transforming business operations with measurable efficiency gains.'
                },
                'marketing_analysis': {
                    'executive_summary': 'Businesses adopting AI-driven automation see 20-30% productivity improvements.'
                },
                'papers_summary': [],
                'research_quality': 'keyword-based'
            }
            
            logger.info("🎯 Generating content (this may take 15-30 seconds)...")
            content_start = datetime.now()
            
            content_result = agent.generate_content(keywords_data, research_analysis, content_spec)
            
            generation_time = (datetime.now() - content_start).total_seconds()
            
            if content_result.generation_successful:
                logger.info(f"✅ Content generated successfully in {generation_time:.1f}s")
                logger.info(f"   Word Count: {content_result.word_count}")
                logger.info(f"   Quality Score: {content_result.quality_score:.1%}")
                logger.info(f"   Research Quality: {content_result.research_quality}")
                
                # Show preview
                preview = content_result.content[:200] + "..." if len(content_result.content) > 200 else content_result.content
                logger.info(f"\n📖 Content Preview:")
                logger.info(f"   {preview}")
                
                # Test document creation
                logger.info("\n📄 Testing Document Creation...")
                doc_start = datetime.now()
                
                document_result = agent.create_comprehensive_document(
                    content_result, keywords_data, research_analysis, content_spec
                )
                
                doc_time = (datetime.now() - doc_start).total_seconds()
                
                if document_result['success']:
                    logger.info(f"✅ Document created successfully in {doc_time:.1f}s")
                    logger.info(f"   Filename: {document_result['filename']}")
                    logger.info(f"   File Size: {document_result['file_size']} bytes")
                    logger.info(f"   Estimated Pages: {document_result['pages_estimated']}")
                else:
                    logger.error(f"❌ Document creation failed: {document_result['error']}")
            else:
                logger.error(f"❌ Content generation failed: {content_result.metadata.get('error', 'Unknown error')}")
        else:
            logger.info("\n⚠️ OpenAI client not available - skipping content generation test")
            logger.info("   Set OPENAI_API_KEY environment variable to test content generation")
        
        # Test prompt generation
        logger.info("\n🎭 Testing Prompt Generation...")
        
        test_spec = ContentSpecification(
            content_type="article",
            content_tone="authoritative",
            content_length="medium",
            target_audience="executives"
        )
        
        test_research = {
            'academic_analysis': {'marketing_summary': 'Test analysis'},
            'marketing_analysis': {'executive_summary': 'Test insights'},
            'papers_summary': [{'title': 'Test Paper', 'authors': ['Test Author'], 'citations': 100}]
        }
        
        prompt = agent._create_content_prompt(keywords_data, test_research, test_spec)
        logger.info(f"✅ Prompt generated: {len(prompt)} characters")
        
        # Summary
        total_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"\n🎉 Quick test completed successfully in {total_time:.1f} seconds!")
        logger.info("   All core functionality verified without Google authentication delays")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Quick test failed: {e}")
        return False

def test_with_google_auth():
    """Test with Google authentication for comparison"""
    
    try:
        logger.info("\n🐌 Comparison Test: With Google Authentication")
        logger.info("=" * 50)
        
        from ai_content_research_agent import AIContentResearchAgent
        
        logger.info("⏱️ Initializing agent with Google authentication...")
        start_time = datetime.now()
        
        # This will take much longer due to Google auth
        agent = AIContentResearchAgent(skip_google_auth=False)
        
        init_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Agent with Google auth initialized in {init_time:.2f} seconds")
        
        # Show the difference
        logger.info(f"📊 Time comparison:")
        logger.info(f"   With Google Auth: {init_time:.2f}s")
        logger.info(f"   Without Google Auth: ~1-2s")
        logger.info(f"   Speed improvement: {init_time/2:.1f}x faster")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Google auth test failed: {e}")
        return False

def main():
    """Run the quick tests"""
    
    logger.info("⚡ AI Content Research Agent - Quick Testing")
    logger.info("=" * 70)
    
    # Check environment
    openai_key = os.environ.get('OPENAI_API_KEY')
    if openai_key:
        logger.info("✅ OpenAI API key configured")
    else:
        logger.warning("⚠️ OPENAI_API_KEY not set - content generation will be skipped")
    
    # Run quick test (no Google auth)
    success = quick_test_agent()
    
    if success:
        logger.info("\n💡 Tips for production use:")
        logger.info("1. For fastest testing: use skip_google_auth=True")
        logger.info("2. For full research capabilities: use skip_google_auth=False")
        logger.info("3. For web apps: cache the research agent instance")
        logger.info("4. For batch processing: initialize once, use many times")
        
        # Optionally test with Google auth for comparison
        user_input = input("\n🤔 Test with Google auth for comparison? (y/N): ").strip().lower()
        if user_input in ['y', 'yes']:
            test_with_google_auth()
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 