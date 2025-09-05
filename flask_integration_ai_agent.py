#!/usr/bin/env python3
"""
Flask Integration for AI Content Research Agent
Shows how to integrate the new agent into the existing Flask application

This replaces the current AI content generation routes in app.py with 
the enhanced AI Content Research Agent functionality.
"""

import os
import json
import logging
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, Any

from flask import Flask, request, jsonify, render_template, redirect, url_for

# Import the new AI Content Research Agent
try:
    from ai_content_research_agent import AIContentResearchAgent, ContentSpecification
    AI_AGENT_AVAILABLE = True
except ImportError:
    AI_AGENT_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global storage for task status and results (same as in app.py)
task_status = {}
task_results = {}

# Initialize the AI Content Research Agent (globally)
ai_content_agent = None

def initialize_ai_content_agent(fast_mode=False):
    """Initialize the AI Content Research Agent"""
    global ai_content_agent
    
    if not AI_AGENT_AVAILABLE:
        logger.error("❌ AI Content Research Agent not available")
        return False
    
    try:
        # Initialize with optional fast mode (skip Google auth for faster testing)
        ai_content_agent = AIContentResearchAgent(skip_google_auth=fast_mode)
        stats = ai_content_agent.get_generation_statistics()
        
        mode_info = "fast mode (no Google auth)" if fast_mode else "full mode (with Google research)"
        logger.info(f"✅ AI Content Research Agent initialized in {mode_info}")
        logger.info(f"   OpenAI Available: {stats['system_status']['openai_available']}")
        logger.info(f"   Research Agent Available: {stats['system_status']['research_agent_available']}")
        logger.info(f"   Document Creation Available: {stats['system_status']['document_creation_available']}")
        logger.info(f"   Google Auth Skipped: {fast_mode}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize AI Content Research Agent: {e}")
        return False

def update_task_status(task_id: str, status: str, message: str, progress: int, step: int):
    """Update task status (same as in app.py)"""
    if task_id in task_status:
        task_status[task_id].update({
            'status': status,
            'message': message,
            'progress': progress,
            'step': step,
            'last_update': time.time()
        })

# Enhanced AI Content Generation Routes
def enhanced_ai_content_generate():
    """Enhanced AI content generation using the new agent"""
    try:
        # Get form data
        google_file_id = request.form.get('google_file_id', '').strip()
        content_type = request.form.get('content_type', 'blog_post')
        content_tone = request.form.get('content_tone', 'professional')
        content_length = request.form.get('content_length', 'medium')
        target_audience = request.form.get('target_audience', 'general')
        additional_instructions = request.form.get('additional_instructions', '').strip()
        
        # Validate input
        if not google_file_id:
            return jsonify({'error': 'Google File ID is required'}), 400
        
        if not ai_content_agent:
            return jsonify({'error': 'AI Content Research Agent not available'}), 500
        
        # Extract actual file ID if full URL is provided
        import re
        if 'docs.google.com' in google_file_id:
            match = re.search(r'/document/d/([a-zA-Z0-9-_]+)', google_file_id)
            if match:
                google_file_id = match.group(1)
            else:
                return jsonify({'error': 'Invalid Google Docs URL format'}), 400
        
        # Generate unique task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task status
        task_status[task_id] = {
            'id': task_id,
            'status': 'starting',
            'message': 'Initializing enhanced AI content generation...',
            'progress': 0,
            'step': 0,
            'total_steps': 5,
            'start_time': time.time(),
            'last_update': time.time(),
            'created_at': datetime.now().isoformat(),
            'details': [],
            'type': 'enhanced_ai_content_generation',
            'content_type': content_type,
            'content_tone': content_tone,
            'content_length': content_length,
            'target_audience': target_audience
        }
        
        # Create content specification
        content_spec = ContentSpecification(
            content_type=content_type,
            content_tone=content_tone,
            content_length=content_length,
            target_audience=target_audience,
            additional_instructions=additional_instructions
        )
        
        # Start background task
        thread = threading.Thread(
            target=run_enhanced_ai_content_process,
            args=(task_id, google_file_id, content_spec)
        )
        thread.daemon = True
        thread.start()
        
        logger.info(f"[AI-AGENT-{task_id}] Started enhanced AI content generation for Google Doc: {google_file_id}")
        
        return jsonify({
            'task_id': task_id,
            'status': 'started',
            'message': 'Enhanced AI content generation started',
            'estimated_time': '3-8 minutes',
            'agent_type': 'AI Content Research Agent'
        })
        
    except Exception as e:
        logger.error(f"Error starting enhanced AI content generation: {e}")
        return jsonify({'error': f'Failed to start enhanced AI content generation: {str(e)}'}), 500

def run_enhanced_ai_content_process(task_id: str, google_file_id: str, content_spec: ContentSpecification):
    """Run enhanced AI content generation process using the new agent"""
    try:
        logger.info(f"[AI-AGENT-{task_id}] Starting enhanced content generation pipeline")
        
        if not ai_content_agent:
            raise Exception("AI Content Research Agent not initialized")
        
        # Step 1: Extract keywords from Google file
        update_task_status(task_id, 'running', 'Extracting keywords from Google Document...', 10, 1)
        logger.info(f"[AI-AGENT-{task_id}] Step 1: Extracting keywords")
        
        keywords_data = ai_content_agent.extract_keywords_from_google_file(google_file_id)
        
        if "error" in keywords_data:
            raise Exception(f"Failed to extract keywords: {keywords_data['error']}")
        
        # Step 2: Conduct research
        update_task_status(task_id, 'running', 'Conducting comprehensive research...', 35, 2)
        logger.info(f"[AI-AGENT-{task_id}] Step 2: Conducting research")
        
        papers = ai_content_agent.conduct_research(keywords_data, max_papers=8)
        
        # Step 3: Analyze research for content
        update_task_status(task_id, 'running', 'Analyzing research for content generation...', 60, 3)
        logger.info(f"[AI-AGENT-{task_id}] Step 3: Analyzing research")
        
        research_analysis = ai_content_agent.analyze_research_for_content(papers, keywords_data)
        
        # Step 4: Generate AI content
        update_task_status(task_id, 'running', 'Generating AI content with research insights...', 80, 4)
        logger.info(f"[AI-AGENT-{task_id}] Step 4: Generating content")
        
        content_result = ai_content_agent.generate_content(keywords_data, research_analysis, content_spec)
        
        if not content_result.generation_successful:
            raise Exception(f"Content generation failed: {content_result.metadata.get('error', 'Unknown error')}")
        
        # Step 5: Create comprehensive document
        update_task_status(task_id, 'running', 'Creating comprehensive Word document...', 95, 5)
        logger.info(f"[AI-AGENT-{task_id}] Step 5: Creating document")
        
        document_result = ai_content_agent.create_comprehensive_document(
            content_result, keywords_data, research_analysis, content_spec
        )
        
        if not document_result['success']:
            raise Exception(f"Document creation failed: {document_result['error']}")
        
        # Store results
        task_results[task_id] = {
            'content_generated': {
                'content': content_result.content,
                'word_count': content_result.word_count,
                'generation_time': content_result.generation_time,
                'quality_score': content_result.quality_score,
                'research_quality': content_result.research_quality,
                'citations_included': content_result.citations_included,
                'generation_successful': content_result.generation_successful
            },
            'final_document': {
                'filename': document_result['filename'],
                'file_size': document_result['file_size'],
                'success': document_result['success']
            },
            'research_summary': {
                'papers_found': len(papers),
                'papers_analyzed': len(papers),
                'keywords_extracted': len(keywords_data.get('primary_keywords', [])),
                'research_quality': research_analysis.get('research_quality', 'unknown')
            },
            'generation_params': {
                'content_type': content_spec.content_type,
                'content_tone': content_spec.content_tone,
                'content_length': content_spec.content_length,
                'target_audience': content_spec.target_audience,
                'additional_instructions': content_spec.additional_instructions
            },
            'agent_stats': ai_content_agent.get_generation_statistics()
        }
        
        # Final completion
        update_task_status(task_id, 'completed', 'Enhanced AI content generation completed successfully!', 100, 5)
        logger.info(f"[AI-AGENT-{task_id}] Enhanced content generation completed successfully")
        
    except Exception as e:
        logger.error(f"[AI-AGENT-{task_id}] Error in enhanced content generation: {e}")
        update_task_status(task_id, 'error', f'Error: {str(e)}', 0, 0)

# Integration function to replace existing routes
def integrate_with_flask_app(app: Flask):
    """
    Integration function to add enhanced AI content generation to existing Flask app
    
    Usage:
        from flask_integration_ai_agent import integrate_with_flask_app, initialize_ai_content_agent
        
        # Initialize the agent
        initialize_ai_content_agent()
        
        # Integrate with your Flask app
        integrate_with_flask_app(app)
    """
    
    # Replace the existing AI content generation route
    @app.route('/ai-content/generate-enhanced', methods=['POST'])
    def ai_content_generate_enhanced():
        return enhanced_ai_content_generate()
    
    # Enhanced status endpoint
    @app.route('/api/ai-content-enhanced/status/<task_id>')
    def api_ai_content_enhanced_status(task_id):
        """Enhanced API endpoint for AI content generation status"""
        try:
            if task_id not in task_status:
                return jsonify({'error': 'Task not found'}), 404
            
            status = task_status[task_id].copy()
            
            # Add timing information
            if 'start_time' in status:
                elapsed_time = time.time() - status['start_time']
                status['elapsed_time'] = round(elapsed_time, 2)
                
                # Estimate remaining time based on progress
                if status['progress'] > 0:
                    estimated_total = elapsed_time / (status['progress'] / 100)
                    remaining = max(0, estimated_total - elapsed_time)
                    status['estimated_remaining'] = round(remaining, 2)
            
            # Add agent statistics if available
            if ai_content_agent:
                status['agent_stats'] = ai_content_agent.get_generation_statistics()
            
            return jsonify(status)
            
        except Exception as e:
            logger.error(f"Error getting enhanced AI content status: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Agent status endpoint
    @app.route('/api/ai-content-agent/status')
    def ai_content_agent_status():
        """Get AI Content Research Agent status"""
        try:
            if not ai_content_agent:
                return jsonify({
                    'available': False,
                    'error': 'AI Content Research Agent not initialized'
                })
            
            stats = ai_content_agent.get_generation_statistics()
            return jsonify({
                'available': True,
                'stats': stats,
                'capabilities': {
                    'content_types': list(ai_content_agent.content_templates.keys()),
                    'research_integration': stats['system_status']['research_agent_available'],
                    'document_creation': stats['system_status']['document_creation_available']
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            return jsonify({'error': str(e)}), 500

# Example of how to update the existing app.py
def example_app_integration():
    """
    Example of how to integrate the enhanced agent into the existing app.py
    """
    
    integration_instructions = """
    # To integrate the AI Content Research Agent into your existing app.py:
    
    1. Add import at the top of app.py:
       from flask_integration_ai_agent import integrate_with_flask_app, initialize_ai_content_agent
    
    2. Initialize the agent in the startup section:
       # Initialize AI Content Research Agent
       if initialize_ai_content_agent():
           logger.info("✅ Enhanced AI Content Research Agent initialized")
           integrate_with_flask_app(app)
       else:
           logger.warning("⚠️ Enhanced AI Content Research Agent not available")
    
    3. Update the AI content generator form to use the new endpoint:
       In templates/ai_content_generator.html, change the form action to:
       fetch('/ai-content/generate-enhanced', { ... })
    
    4. Update progress tracking to use the new status endpoint:
       fetch(`/api/ai-content-enhanced/status/${taskId}`)
    
    5. The enhanced agent provides:
       - Better research integration with Google Scholar
       - More sophisticated content generation prompts
       - Comprehensive Word document creation
       - Advanced quality scoring
       - Detailed generation statistics
    """
    
    print(integration_instructions)

if __name__ == "__main__":
    # Test the integration
    print("🧪 Testing AI Content Research Agent Flask Integration")
    print("=" * 60)
    
    # Initialize agent
    if initialize_ai_content_agent():
        print("✅ Agent initialized successfully")
        
        # Show capabilities
        if ai_content_agent:
            stats = ai_content_agent.get_generation_statistics()
            print(f"📊 Agent Statistics:")
            print(f"   OpenAI Available: {stats['system_status']['openai_available']}")
            print(f"   Research Available: {stats['system_status']['research_agent_available']}")
            print(f"   Document Creation: {stats['system_status']['document_creation_available']}")
            print(f"   Content Templates: {stats['content_templates_loaded']}")
        
        print("\n📖 Integration Instructions:")
        example_app_integration()
        
    else:
        print("❌ Agent initialization failed")
        print("   Check dependencies and configuration") 