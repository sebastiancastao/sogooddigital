#!/usr/bin/env python3
"""
Example Usage of AI Content Research Agent
Demonstrates how to integrate the agent into your applications
"""

import os
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def example_blog_post_generation():
    """Example: Generate a blog post using the AI Content Research Agent"""
    
    try:
        from ai_content_research_agent import AIContentResearchAgent, ContentSpecification
        
        logger.info("🚀 Example: Blog Post Generation")
        logger.info("=" * 40)
        
        # Initialize the agent
        agent = AIContentResearchAgent()
        
        # Check system status
        stats = agent.get_generation_statistics()
        logger.info(f"OpenAI Available: {stats['system_status']['openai_available']}")
        logger.info(f"Research Agent Available: {stats['system_status']['research_agent_available']}")
        
        # Define content specifications
        content_spec = ContentSpecification(
            content_type="blog_post",
            content_tone="professional",
            content_length="medium",
            target_audience="business_professionals",
            additional_instructions="Focus on practical implementation strategies and real-world examples"
        )
        
        # Example keywords data (normally extracted from Google Doc)
        keywords_data = {
            'primary_keywords': [
                'artificial intelligence', 'business automation', 'digital transformation',
                'machine learning', 'productivity tools'
            ],
            'secondary_keywords': [
                'efficiency', 'innovation', 'technology adoption'
            ],
            'research_topics': [
                'AI implementation strategies', 'business process automation',
                'digital transformation frameworks'
            ],
            'marketing_keywords': [
                'AI solutions', 'automation tools', 'digital innovation'
            ],
            'business_terms': [
                'operational efficiency', 'competitive advantage', 'strategic implementation'
            ]
        }
        
        # Example research analysis (normally from research papers)
        research_analysis = {
            'academic_analysis': {
                'marketing_summary': """
                Recent research indicates that businesses implementing AI-driven automation 
                see average productivity improvements of 25-40%. Key success factors include 
                strategic planning, employee training, and gradual implementation approaches.
                Studies show that companies with structured AI adoption frameworks are 
                3x more likely to achieve their digital transformation goals.
                """
            },
            'marketing_analysis': {
                'executive_summary': """
                Market analysis reveals growing demand for AI automation solutions across 
                industries. Early adopters gain significant competitive advantages through 
                improved efficiency, reduced costs, and enhanced customer experiences. 
                The AI automation market is projected to grow 25% annually through 2027.
                """
            },
            'papers_summary': [
                {
                    'title': 'AI-Driven Business Process Automation: A Systematic Review',
                    'authors': ['Smith, J.', 'Johnson, A.', 'Williams, R.'],
                    'abstract': 'Comprehensive analysis of AI automation implementations...',
                    'citations': 245,
                    'business_relevance': 'Provides framework for successful AI implementation'
                },
                {
                    'title': 'Digital Transformation Strategies in Modern Enterprises',
                    'authors': ['Brown, M.', 'Davis, S.'],
                    'abstract': 'Strategic approaches to digital transformation...',
                    'citations': 189,
                    'business_relevance': 'Outlines best practices for transformation initiatives'
                }
            ],
            'research_quality': 'high'
        }
        
        logger.info("📝 Generating content...")
        
        # Generate content
        content_result = agent.generate_content(keywords_data, research_analysis, content_spec)
        
        if content_result.generation_successful:
            logger.info("✅ Content generation successful!")
            logger.info(f"   Word count: {content_result.word_count}")
            logger.info(f"   Generation time: {content_result.generation_time:.2f}s")
            logger.info(f"   Quality score: {content_result.quality_score:.1%}")
            logger.info(f"   Research papers used: {content_result.research_papers_used}")
            
            # Show content preview
            logger.info("\n📖 Content Preview:")
            logger.info("-" * 30)
            preview = content_result.content[:500] + "..." if len(content_result.content) > 500 else content_result.content
            logger.info(preview)
            
            # Create document
            logger.info("\n📄 Creating Word document...")
            document_result = agent.create_comprehensive_document(
                content_result, keywords_data, research_analysis, content_spec
            )
            
            if document_result['success']:
                logger.info(f"✅ Document created: {document_result['filename']}")
                logger.info(f"   File size: {document_result['file_size']} bytes")
                logger.info(f"   Estimated pages: {document_result['pages_estimated']}")
            else:
                logger.error(f"❌ Document creation failed: {document_result['error']}")
                
        else:
            logger.error("❌ Content generation failed!")
            logger.error(f"   Error: {content_result.metadata.get('error', 'Unknown error')}")
            
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.info("   Make sure ai_content_research_agent.py is in the same directory")
    except Exception as e:
        logger.error(f"❌ Example failed: {e}")

def example_complete_pipeline():
    """Example: Run complete pipeline from Google Doc to content"""
    
    try:
        from ai_content_research_agent import AIContentResearchAgent, ContentSpecification
        
        logger.info("\n🎯 Example: Complete Research-to-Content Pipeline")
        logger.info("=" * 50)
        
        # Initialize agent
        agent = AIContentResearchAgent()
        
        # Content specification
        content_spec = ContentSpecification(
            content_type="article",
            content_tone="authoritative",
            content_length="long",
            target_audience="executives",
            additional_instructions="Include data-driven insights and strategic recommendations"
        )
        
        # Note: This would use a real Google Doc ID in practice
        logger.info("📋 Example pipeline steps:")
        logger.info("1. Extract keywords from Google Doc")
        logger.info("2. Search for relevant research papers")
        logger.info("3. Analyze research for business insights")
        logger.info("4. Generate AI content based on research")
        logger.info("5. Create comprehensive Word document")
        
        # Uncomment to test with actual Google Doc:
        # google_file_id = "your-google-doc-id-here"
        # result = agent.run_complete_content_pipeline(google_file_id, content_spec)
        
        logger.info("💡 To run the complete pipeline, provide a Google Doc ID:")
        logger.info("   result = agent.run_complete_content_pipeline('your-doc-id', content_spec)")
        
    except Exception as e:
        logger.error(f"❌ Pipeline example failed: {e}")

def example_integration_with_flask():
    """Example: How to integrate with Flask application"""
    
    logger.info("\n🌐 Example: Flask Integration")
    logger.info("=" * 30)
    
    integration_code = '''
# In your Flask app:

from ai_content_research_agent import AIContentResearchAgent, ContentSpecification

# Initialize agent (do this once at app startup)
content_agent = AIContentResearchAgent()

@app.route('/generate-content', methods=['POST'])
def generate_content():
    """Generate content using the AI Content Research Agent"""
    
    # Get parameters from form
    google_file_id = request.form.get('google_file_id')
    content_type = request.form.get('content_type', 'blog_post')
    tone = request.form.get('tone', 'professional')
    length = request.form.get('length', 'medium')
    audience = request.form.get('audience', 'general')
    instructions = request.form.get('instructions', '')
    
    # Create content specification
    content_spec = ContentSpecification(
        content_type=content_type,
        content_tone=tone,
        content_length=length,
        target_audience=audience,
        additional_instructions=instructions
    )
    
    # Run complete pipeline
    result = content_agent.run_complete_content_pipeline(google_file_id, content_spec)
    
    if result['success']:
        return jsonify({
            'success': True,
            'document_filename': result['document_result']['filename'],
            'word_count': result['content_result'].word_count,
            'generation_time': result['pipeline_time']
        })
    else:
        return jsonify({
            'success': False,
            'error': result['error']
        })
    '''
    
    logger.info("Flask integration example:")
    logger.info(integration_code)

def main():
    """Run all examples"""
    logger.info("📚 AI Content Research Agent - Usage Examples")
    logger.info("=" * 60)
    
    # Check environment
    openai_key = os.environ.get('OPENAI_API_KEY')
    if not openai_key:
        logger.warning("⚠️ OPENAI_API_KEY not set - content generation will not work")
        logger.info("   Set with: export OPENAI_API_KEY='your-api-key'")
    else:
        logger.info("✅ OpenAI API key configured")
    
    # Run examples
    try:
        example_blog_post_generation()
        example_complete_pipeline()
        example_integration_with_flask()
        
        logger.info("\n🎉 Examples completed successfully!")
        logger.info("\n💡 Next Steps:")
        logger.info("1. Set up your OpenAI API key")
        logger.info("2. Test with: python test_ai_content_research_agent.py")
        logger.info("3. Integrate into your Flask application")
        logger.info("4. Use agent.run_complete_content_pipeline() for full automation")
        
    except Exception as e:
        logger.error(f"❌ Examples failed: {e}")

if __name__ == "__main__":
    main() 