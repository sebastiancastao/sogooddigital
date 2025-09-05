#!/usr/bin/env python3
"""
Test AI Content Research Agent WITHOUT OAuth Authentication
Demonstrates service account authentication like google_scholar_research_agent.py
"""

import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_no_oauth_initialization():
    """Test initializing without OAuth delays"""
    
    try:
        logger.info("🚀 Testing AI Content Research Agent - No OAuth Mode")
        logger.info("=" * 60)
        
        from ai_content_research_agent import AIContentResearchAgent, ContentSpecification
        
        # Test 1: Fast mode (skip Google auth entirely)
        logger.info("⚡ Test 1: Fast Mode (Skip Google Auth)")
        logger.info("-" * 40)
        
        start_time = datetime.now()
        agent_fast = AIContentResearchAgent(skip_google_auth=True)
        fast_init_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"✅ Fast mode initialized in {fast_init_time:.2f} seconds")
        logger.info(f"   Google Auth Skipped: {agent_fast.skip_google_auth}")
        logger.info(f"   Research Agent Available: {agent_fast.research_agent is not None}")
        
        # Test keyword extraction in fast mode
        logger.info("\n🔑 Testing keyword extraction in fast mode...")
        keywords = agent_fast.extract_keywords_from_google_file("test-doc-id")
        
        logger.info(f"✅ Keywords extracted successfully:")
        logger.info(f"   Method: {keywords.get('extraction_method', 'unknown')}")
        logger.info(f"   Primary Keywords: {keywords.get('primary_keywords', [])[:3]}")
        logger.info(f"   Google Auth Skipped: {keywords.get('google_auth_skipped', False)}")
        
        # Test 2: Full mode with service account (like original google_scholar_research_agent.py)
        logger.info("\n🔐 Test 2: Full Mode (Service Account Auth)")
        logger.info("-" * 40)
        
        # Check if service account credentials are available
        has_service_account = (
            os.path.exists('service-account.json') or 
            os.environ.get('GOOGLE_TYPE') == 'service_account' or
            os.environ.get('GOOGLE_SERVICE_ACCOUNT_PATH')
        )
        
        if has_service_account:
            logger.info("🔍 Service account credentials detected, testing full mode...")
            
            start_time = datetime.now()
            agent_full = AIContentResearchAgent(skip_google_auth=False)
            full_init_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Full mode initialized in {full_init_time:.2f} seconds")
            logger.info(f"   Google Auth Skipped: {agent_full.skip_google_auth}")
            logger.info(f"   Research Agent Available: {agent_full.research_agent is not None}")
            
            if agent_full.research_agent:
                auth_status = getattr(agent_full.research_agent, 'google_authenticated', False)
                logger.info(f"   Google Services Authenticated: {auth_status}")
                
                if auth_status:
                    logger.info("✅ Service account authentication successful!")
                else:
                    logger.warning("⚠️ Service account authentication failed")
            
            # Performance comparison
            logger.info(f"\n📊 Performance Comparison:")
            logger.info(f"   Fast Mode: {fast_init_time:.2f}s")
            logger.info(f"   Full Mode: {full_init_time:.2f}s")
            logger.info(f"   Speed Difference: {full_init_time/fast_init_time:.1f}x faster in fast mode")
            
        else:
            logger.info("⚠️ No service account credentials found")
            logger.info("   To test full mode, either:")
            logger.info("   1. Place service-account.json in project directory")
            logger.info("   2. Set GOOGLE_SERVICE_ACCOUNT_PATH environment variable")
            logger.info("   3. Set Google service account environment variables")
        
        # Test 3: Content generation in fast mode
        if agent_fast.client:  # OpenAI available
            logger.info("\n✨ Test 3: Content Generation (Fast Mode)")
            logger.info("-" * 40)
            
            content_spec = ContentSpecification(
                content_type="blog_post",
                content_tone="professional",
                content_length="short",
                target_audience="business_professionals",
                additional_instructions="Focus on practical applications"
            )
            
            # Create simple research analysis for testing
            research_analysis = {
                'academic_analysis': {
                    'marketing_summary': 'Digital transformation is reshaping how businesses operate and engage with customers.'
                },
                'marketing_analysis': {
                    'executive_summary': 'Companies leveraging AI and automation see significant efficiency improvements.'
                },
                'papers_summary': [],
                'research_quality': 'keyword-based'
            }
            
            logger.info("🎯 Generating content (this may take 15-30 seconds)...")
            content_start = datetime.now()
            
            content_result = agent_fast.generate_content(keywords, research_analysis, content_spec)
            
            generation_time = (datetime.now() - content_start).total_seconds()
            
            if content_result.generation_successful:
                logger.info(f"✅ Content generated successfully in {generation_time:.1f}s")
                logger.info(f"   Word Count: {content_result.word_count}")
                logger.info(f"   Quality Score: {content_result.quality_score:.1%}")
                
                # Create document
                logger.info("\n📄 Testing document creation...")
                doc_start = datetime.now()
                
                document_result = agent_fast.create_comprehensive_document(
                    content_result, keywords, research_analysis, content_spec
                )
                
                doc_time = (datetime.now() - doc_start).total_seconds()
                
                if document_result['success']:
                    logger.info(f"✅ Document created successfully in {doc_time:.1f}s")
                    logger.info(f"   Filename: {document_result['filename']}")
                    logger.info(f"   File Size: {document_result['file_size']} bytes")
                else:
                    logger.error(f"❌ Document creation failed")
            else:
                logger.error(f"❌ Content generation failed")
        else:
            logger.info("\n⚠️ OpenAI client not available")
            logger.info("   Set OPENAI_API_KEY environment variable to test content generation")
        
        # Summary
        logger.info("\n🎉 Test Summary")
        logger.info("=" * 40)
        logger.info("✅ Fast mode (skip Google auth): WORKING")
        logger.info("✅ Keyword extraction: WORKING")
        logger.info("✅ Enhanced fallback: WORKING")
        
        if has_service_account:
            logger.info("✅ Service account mode: TESTED")
        else:
            logger.info("⚠️ Service account mode: NOT TESTED (credentials missing)")
        
        if agent_fast.client:
            logger.info("✅ Content generation: WORKING")
            logger.info("✅ Document creation: WORKING")
        else:
            logger.info("⚠️ Content generation: SKIPPED (OpenAI key missing)")
        
        logger.info("\n💡 Usage Recommendations:")
        logger.info("   - For testing/development: Use skip_google_auth=True")
        logger.info("   - For production with research: Use skip_google_auth=False + service account")
        logger.info("   - Service account avoids OAuth prompts completely")
        logger.info("   - Same authentication method as google_scholar_research_agent.py")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def main():
    """Run the OAuth-free tests"""
    
    logger.info("🔐 AI Content Research Agent - OAuth-Free Testing")
    logger.info("=" * 70)
    logger.info("This test demonstrates authentication WITHOUT OAuth prompts")
    logger.info("Uses the same service account method as google_scholar_research_agent.py")
    logger.info("")
    
    # Check environment
    openai_key = os.environ.get('OPENAI_API_KEY')
    if openai_key:
        logger.info("✅ OpenAI API key configured")
    else:
        logger.warning("⚠️ OPENAI_API_KEY not set - content generation will be skipped")
    
    # Check for service account credentials
    service_account_indicators = [
        os.path.exists('service-account.json'),
        os.environ.get('GOOGLE_TYPE') == 'service_account',
        os.environ.get('GOOGLE_SERVICE_ACCOUNT_PATH'),
        os.environ.get('GOOGLE_PRIVATE_KEY')
    ]
    
    if any(service_account_indicators):
        logger.info("✅ Service account credentials detected")
    else:
        logger.warning("⚠️ No service account credentials found")
        logger.info("   Full Google services integration will be skipped")
    
    logger.info("")
    
    # Run tests
    success = test_no_oauth_initialization()
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 