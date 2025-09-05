#!/usr/bin/env python3
"""
AI Content Research Agent
Combines Google Scholar research capabilities with AI-powered content generation

This agent extends the functionality of GoogleScholarResearchAgent by adding:
- Advanced content generation using OpenAI
- Multiple content format support
- Research-driven content creation
- Professional document generation
"""

import os
import json
import logging
import time
import re
import requests
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import threading
from collections import Counter

# Import base research agent
try:
    from google_scholar_research_agent import GoogleScholarResearchAgent, ResearchPaper
    RESEARCH_AGENT_AVAILABLE = True
except ImportError:
    GoogleScholarResearchAgent = None
    ResearchPaper = None
    RESEARCH_AGENT_AVAILABLE = False

# Import document creation libraries
try:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Inches
    DOC_CREATION_AVAILABLE = True
except ImportError:
    DOC_CREATION_AVAILABLE = False

# Import OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ContentSpecification:
    """Data class for content generation specifications"""
    content_type: str = "blog_post"  # blog_post, article, social_media, etc.
    content_tone: str = "professional"  # professional, casual, authoritative, etc.
    content_length: str = "medium"  # short, medium, long
    target_audience: str = "general"  # general, business_professionals, etc.
    additional_instructions: str = ""
    language: str = "en"
    include_citations: bool = True
    include_statistics: bool = True
    seo_optimization: bool = True

# @dataclass
# class ImageGenerationResult:
#     """Data class for AI image generation results"""
#     image_url: str = ""
#     image_prompt: str = ""
#     image_filename: str = ""
#     generation_successful: bool = False
#     generation_time: float = 0.0
#     image_style: str = "minimalistic"
#     concept_extracted: str = ""
#     error_message: str = ""
#     metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContentResult:
    """Data class for generated content results"""
    content: str = ""
    content_type: str = ""
    word_count: int = 0
    generation_successful: bool = False
    research_papers_used: int = 0
    keywords_used: int = 0
    generation_time: float = 0.0
    quality_score: float = 0.0
    research_quality: str = "unknown"
    citations_included: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    # generated_image: Optional[ImageGenerationResult] = None

class AIContentResearchAgent:
    """
    Advanced AI Content Research Agent
    Combines comprehensive research capabilities with AI-powered content generation
    """
    
    def __init__(self, 
                 openai_api_key: str = None,
                 google_credentials_path: str = None,
                 model_name: str = "gpt-4o",
                 enable_research: bool = True,
                 skip_google_auth: bool = False):
        """
        Initialize the AI Content Research Agent
        
        Args:
            openai_api_key: OpenAI API key for content generation
            google_credentials_path: Path to Google service account credentials
            model_name: OpenAI model to use for content generation
            enable_research: Whether to enable Google Scholar research integration
            skip_google_auth: Skip Google authentication for faster initialization (testing)
        """
        # Initialize OpenAI
        self.openai_api_key = openai_api_key or os.environ.get('OPENAI_API_KEY')
        self.model_name = model_name
        self.client = None
        self.enable_research = enable_research
        self.skip_google_auth = skip_google_auth
        
        if OPENAI_AVAILABLE and self.openai_api_key:
            try:
                self.client = openai.OpenAI(api_key=self.openai_api_key)
                logger.info("✅ OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize OpenAI client: {e}")
        
        # Initialize research agent if available and enabled
        self.research_agent = None
        if RESEARCH_AGENT_AVAILABLE and enable_research and not skip_google_auth:
            try:
                # Check if we already have a cached research agent
                if not hasattr(AIContentResearchAgent, '_cached_research_agent'):
                    logger.info("🔄 Initializing research agent with service account authentication...")
                    
                    # Force service account authentication (no OAuth)
                    research_agent = GoogleScholarResearchAgent(
                        openai_api_key=self.openai_api_key,
                        google_credentials_path=google_credentials_path
                    )
                    
                    # Verify that it's using service account, not OAuth
                    if hasattr(research_agent, 'google_authenticated') and research_agent.google_authenticated:
                        AIContentResearchAgent._cached_research_agent = research_agent
                        logger.info("✅ Research agent initialized with service account and cached")
                    else:
                        logger.warning("⚠️ Research agent failed to authenticate with service account")
                        AIContentResearchAgent._cached_research_agent = None
                else:
                    logger.info("✅ Using cached research agent (service account)")
                
                self.research_agent = AIContentResearchAgent._cached_research_agent
                
            except Exception as e:
                logger.warning(f"⚠️ Research agent initialization failed: {e}")
                logger.info("💡 Make sure service-account.json exists or Google environment variables are set")
                self.research_agent = None
        elif skip_google_auth:
            logger.info("⏭️ Skipping Google authentication for faster initialization")
        elif not enable_research:
            logger.info("🚫 Research integration disabled")
        
        # Content generation templates
        self.content_templates = self._load_content_templates()
        
        # Load B2B marketing content generator
        try:
            from b2b_marketing_content_spec import B2BMarketingContentGenerator, B2BMarketingContentSpec, create_b2b_marketing_prompt
            self.b2b_generator = B2BMarketingContentGenerator()
            self.B2BMarketingContentSpec = B2BMarketingContentSpec
            self.b2b_prompt_creator = create_b2b_marketing_prompt
            logger.info("✅ B2B Marketing Content Generator loaded")
        except ImportError as e:
            logger.warning(f"⚠️ B2B Marketing Content Generator not available: {e}")
            self.b2b_generator = None
            self.B2BMarketingContentSpec = None
            self.b2b_prompt_creator = None
        
        # Content generation statistics
        self.generation_stats = {
            'total_generated': 0,
            'successful_generations': 0,
            'average_generation_time': 0.0,
            'content_types_generated': {},
            'images_generated': 0,
            'successful_image_generations': 0
        }
        
        # Image generation settings (DISABLED)
        # self.image_generation_enabled = True
        # self.image_model = "dall-e-3"
        # self.image_size = "1024x1024"
        # self.image_quality = "standard"
    
    def _load_content_templates(self) -> Dict[str, Dict]:
        """Load content generation templates and configurations"""
        return {
            'blog_post': {
                'word_ranges': {'short': '800-1200', 'medium': '1200-1800', 'long': '1800-2500'},
                'structure': ['headline', 'introduction', 'main_sections', 'conclusion', 'cta'],
                'seo_elements': ['title_tag', 'meta_description', 'headings', 'internal_links']
            },
            'article': {
                'word_ranges': {'short': '1000-1500', 'medium': '1500-2500', 'long': '2500-4000'},
                'structure': ['title', 'executive_summary', 'analysis_sections', 'recommendations', 'references'],
                'academic_elements': ['abstract', 'methodology', 'findings', 'discussion']
            },
            'social_media': {
                'platforms': {'short': 'twitter', 'medium': 'linkedin', 'long': 'multi_platform'},
                'elements': ['hook', 'value_proposition', 'cta', 'hashtags'],
                'character_limits': {'twitter': 280, 'linkedin': 3000, 'facebook': 2200}
            },
            'marketing_copy': {
                'formats': {'short': 'ads_headlines', 'medium': 'landing_page', 'long': 'campaign'},
                'elements': ['headline', 'value_prop', 'benefits', 'social_proof', 'cta'],
                'conversion_focus': ['urgency', 'scarcity', 'testimonials', 'guarantees']
            },
            'whitepaper': {
                'word_ranges': {'short': '2000-3000', 'medium': '3000-5000', 'long': '5000-8000'},
                'structure': ['executive_summary', 'problem_statement', 'solution', 'case_studies', 'conclusion'],
                'academic_rigor': ['citations', 'data_analysis', 'methodology', 'peer_review']
            },
            'email_campaign': {
                'sequence_length': {'short': 3, 'medium': 5, 'long': 7},
                'email_types': ['welcome', 'nurture', 'educational', 'promotional', 'retention'],
                'elements': ['subject_line', 'preview_text', 'body', 'cta', 'signature']
            },
            'press_release': {
                'structure': ['headline', 'dateline', 'lead', 'body_paragraphs', 'boilerplate', 'contact'],
                'news_angles': ['announcement', 'milestone', 'partnership', 'research_findings'],
                'distribution_ready': True
            },
            'case_study': {
                'structure': ['executive_summary', 'challenge', 'solution', 'implementation', 'results', 'conclusion'],
                'proof_elements': ['metrics', 'testimonials', 'before_after', 'roi_analysis'],
                'credibility_factors': ['client_logos', 'data_visualization', 'quotes']
            },
            'b2b_blog_package': {
                'word_ranges': {'short': '800-1000', 'medium': '1000-1200', 'long': '1200-1500'},
                'structure': ['intro', 'market_shift', 'authoritative_stats', 'practical_framework', 'case_proof', 'urgency_cta'],
                'required_elements': ['faq_block', 'author_line', 'authority_citations'],
                'compliance_rules': ['no_emojis', 'authority_sources_only', 'banned_domains_check']
            },
            'b2b_linkedin_post': {
                'word_limit': 150,
                'structure': ['hook', 'value_stat', 'insight', 'cta'],
                'required_elements': ['strategic_angle', 'data_point'],
                'compliance_rules': ['no_emojis', 'authority_sources_only', 'word_limit_strict']
            }
        }
    
    def extract_keywords_from_google_file(self, file_id: str) -> Dict[str, Any]:
        """
        Extract keywords from Google file using the research agent
        
        Args:
            file_id: Google file ID
            
        Returns:
            Dictionary containing extracted keywords and metadata
        """
        if self.skip_google_auth:
            logger.info("🔄 Google authentication skipped, using enhanced fallback keyword extraction")
            return self._extract_keywords_enhanced_fallback(file_id)
        
        if self.research_agent:
            try:
                return self.research_agent.extract_keywords_from_google_file(file_id)
            except Exception as e:
                logger.error(f"Research agent keyword extraction failed: {e}")
        
        # Fallback to simple extraction
        logger.warning("Using fallback keyword extraction")
        return self._extract_keywords_fallback()
    
    def _extract_keywords_fallback(self) -> Dict[str, Any]:
        """Fallback keyword extraction when research agent is not available"""
        return {
            'primary_keywords': ['business', 'strategy', 'marketing', 'research', 'analysis'],
            'secondary_keywords': ['digital', 'innovation', 'technology', 'growth'],
            'research_topics': ['business strategy', 'market analysis'],
            'marketing_keywords': ['marketing', 'strategy', 'business'],
            'business_terms': ['strategy', 'analysis', 'research'],
            'extraction_method': 'fallback_default'
        }
    
    def _extract_keywords_enhanced_fallback(self, file_id: str) -> Dict[str, Any]:
        """Enhanced fallback keyword extraction with file_id simulation"""
        
        # Simulate more sophisticated keyword extraction based on file_id patterns
        business_keywords = [
            'artificial intelligence', 'digital transformation', 'business automation',
            'machine learning', 'data analytics', 'customer experience',
            'operational efficiency', 'competitive advantage', 'innovation strategy'
        ]
        
        tech_keywords = [
            'technology adoption', 'digital solutions', 'automation tools',
            'cloud computing', 'software integration', 'process optimization'
        ]
        

        
        marketing_keywords = [
            'content marketing', 'digital marketing', 'brand strategy',
            'customer engagement', 'market research', 'social media'
        ]
        
        # Create a more sophisticated fallback based on common business topics
        return {
            'primary_keywords': business_keywords[:6],
            'secondary_keywords': tech_keywords[:4],
            'research_topics': [
                'digital transformation strategies',
                'AI implementation in business',
                'automation and efficiency',
                'customer experience optimization'
            ],
            'marketing_keywords': marketing_keywords[:5],
            'business_terms': [
                'strategic implementation', 'operational excellence', 
                'competitive differentiation', 'market leadership'
            ],
            'content_length': 0,  # Unknown without actual file access
            'keyword_density': 0.05,
            'extraction_method': 'enhanced_fallback_simulation',
            'file_id_provided': file_id,
            'google_auth_skipped': True
        }
    
    def conduct_research(self, keywords_data: Dict[str, Any], max_papers: int = 10) -> List[Any]:
        """
        Conduct research based on extracted keywords
        
        Args:
            keywords_data: Keywords extracted from source document
            max_papers: Maximum number of papers to search for
            
        Returns:
            List of research papers
        """
        if self.skip_google_auth:
            logger.info("🔄 Google authentication skipped, returning empty research results")
            return []
        
        if not self.research_agent:
            logger.warning("⚠️ Research agent not available, proceeding without research papers")
            return []
        
        # Verify research agent is properly authenticated
        if not (hasattr(self.research_agent, 'google_authenticated') and self.research_agent.google_authenticated):
            logger.warning("⚠️ Research agent not authenticated with Google services")
            return []
        
        try:
            # Create search queries from keywords
            search_queries = []
            search_queries.extend(keywords_data.get("primary_keywords", [])[:3])
            search_queries.extend(keywords_data.get("research_topics", [])[:2])
            
            logger.info(f"🔍 Searching for papers with {len(search_queries)} queries...")
            
            # Search for papers
            papers = self.research_agent.search_google_scholar(search_queries)
            
            if papers:
                # Filter and rank papers
                filtered_papers = self.research_agent.filter_and_rank_papers(papers, " ".join(search_queries))
                
                # Process papers for additional insights
                processed_papers = self.research_agent.download_and_process_pdfs(filtered_papers[:max_papers])
                
                logger.info(f"Research completed: {len(processed_papers)} papers processed")
                return processed_papers
            else:
                logger.warning("No research papers found")
                return []
                
        except Exception as e:
            logger.error(f"Research process failed: {e}")
            return []
    
    def analyze_research_for_content(self, papers: List[Any], keywords_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze research findings for content generation
        
        Args:
            papers: List of research papers
            keywords_data: Keywords data
            
        Returns:
            Analysis results for content generation
        """
        if not self.research_agent or not papers:
            return self._create_fallback_analysis(keywords_data)
        
        try:
            # Use research agent's analysis capabilities
            analysis_data = self.research_agent.analyze_research_content(papers)
            marketing_analysis = self.research_agent.analyze_marketing_relevance(keywords_data, papers)
            
            return {
                'academic_analysis': analysis_data,
                'marketing_analysis': marketing_analysis,
                'papers_summary': self._create_papers_summary(papers),
                'research_quality': 'high' if len(papers) > 3 else 'medium'
            }
            
        except Exception as e:
            logger.error(f"Research analysis failed: {e}")
            return self._create_fallback_analysis(keywords_data)
    
    def _create_fallback_analysis(self, keywords_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback analysis when research is not available"""
        return {
            'academic_analysis': {
                'marketing_summary': f"Analysis based on keywords: {', '.join(keywords_data.get('primary_keywords', [])[:5])}",
                'key_insights': ['Keyword-based content generation', 'Market-focused approach'],
                'research_quality': 'keyword-based'
            },
            'marketing_analysis': {
                'executive_summary': 'Content generated using keyword analysis and best practices',
                'business_applications': ['Content marketing', 'Thought leadership', 'Audience engagement']
            },
            'papers_summary': [],
            'research_quality': 'keyword-based'
        }
    
    def _create_papers_summary(self, papers: List[Any]) -> List[Dict[str, Any]]:
        """Create a summary of research papers for content generation"""
        return [
            {
                'title': paper.title,
                'authors': paper.authors[:3],  # Limit authors
                'abstract': paper.abstract[:300] + "..." if len(paper.abstract) > 300 else paper.abstract,
                'key_findings': getattr(paper, 'key_findings', [])[:3],
                'business_relevance': getattr(paper, 'business_relevance', ''),
                'citations': paper.citations,
                'relevance_score': getattr(paper, 'relevance_score', 0)
            } for paper in papers[:5]  # Top 5 papers
        ]
    
    def generate_b2b_marketing_content(self,
                                     keyword: str,
                                     keywords_data: Dict[str, Any],
                                     research_analysis: Dict[str, Any],
                                     b2b_spec: Any = None) -> ContentResult:
        """
        Generate B2B marketing content following authority-first sourcing workflow
        
        Args:
            keyword: Single keyword or keyword phrase
            keywords_data: Extracted keywords data
            research_analysis: Research analysis results
            b2b_spec: B2BMarketingContentSpec instance
            
        Returns:
            ContentResult with B2B marketing content
        """
        start_time = time.time()
        
        if not self.client:
            return ContentResult(
                content="Error: OpenAI client not available",
                generation_successful=False,
                metadata={'error': 'OpenAI client not initialized'}
            )
        
        if not self.b2b_generator or not b2b_spec:
            return ContentResult(
                content="Error: B2B Marketing Content Generator not available",
                generation_successful=False,
                metadata={'error': 'B2B generator not initialized'}
            )
        
        try:
            logger.info(f"🚀 Starting B2B marketing content generation for keyword: {keyword}")
            
            # Use specialized B2B content generator
            b2b_result = self.b2b_generator.generate_b2b_content(keyword, research_analysis, b2b_spec)
            
            if not b2b_result.generation_successful:
                return ContentResult(
                    content=f"B2B content generation failed: {'; '.join(b2b_result.errors)}",
                    generation_successful=False,
                    metadata={'errors': b2b_result.errors}
                )
            
            # Combine all content sections
            full_content = f"{b2b_result.blog_body}\n\n{b2b_result.faq_section}\n\n{b2b_result.author_line}"
            
            if b2b_result.linkedin_post:
                full_content = f"LinkedIn Post:\n{b2b_result.linkedin_post}\n\n---\n\nBlog Package:\n{full_content}"
            
            generation_time = time.time() - start_time
            
            # Update statistics
            self._update_generation_stats('b2b_blog_package', generation_time, True)
            
            result = ContentResult(
                content=full_content,
                content_type='b2b_blog_package',
                word_count=b2b_result.word_count,
                generation_successful=True,
                research_papers_used=len(research_analysis.get('papers_summary', [])),
                keywords_used=len(keywords_data.get('primary_keywords', [])),
                generation_time=generation_time,
                quality_score=0.95 if all(b2b_result.compliance_check.values()) else 0.75,
                research_quality=research_analysis.get('research_quality', 'high'),
                citations_included=[stat['source_title'] for stat in b2b_result.evidence_ledger.statistics],
                metadata={
                    'b2b_compliance_check': b2b_result.compliance_check,
                    'concept_hierarchy': b2b_result.concept_hierarchy.concepts,
                    'evidence_ledger': len(b2b_result.evidence_ledger.statistics),
                    'linkedin_post': b2b_result.linkedin_post,
                    'faq_section': b2b_result.faq_section,
                    'author_line': b2b_result.author_line,
                    'keyword': keyword,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Generate conceptual image if enabled (DISABLED)
            # if self.image_generation_enabled:
            #     logger.info("🎨 Generating conceptual image for B2B content...")
            #     image_result = self.generate_conceptual_image(full_content, b2b_spec.content_type, keywords_data)
            #     result.generated_image = image_result
            
            # Add external links to B2B content
            logger.info("🔗 Adding external links to B2B content...")
            linked_content = self.add_external_links_to_content(full_content, keywords_data)
            result.content = linked_content
            
            logger.info(f"✅ B2B marketing content generated successfully: {b2b_result.word_count} words")
            logger.info(f"📊 Compliance checks: {sum(b2b_result.compliance_check.values())}/{len(b2b_result.compliance_check)} passed")
            
            return result
            
        except Exception as e:
            logger.error(f"B2B marketing content generation failed: {e}")
            self._update_generation_stats('b2b_blog_package', time.time() - start_time, False)
            
            return ContentResult(
                content=f"Error generating B2B marketing content: {str(e)}",
                content_type='b2b_blog_package',
                generation_successful=False,
                generation_time=time.time() - start_time,
                metadata={'error': str(e)}
            )

    def generate_content(self, 
                        keywords_data: Dict[str, Any],
                        research_analysis: Dict[str, Any],
                        content_spec: ContentSpecification) -> ContentResult:
        """
        Generate AI content based on research and specifications
        
        Args:
            keywords_data: Extracted keywords
            research_analysis: Research analysis results
            content_spec: Content generation specifications
            
        Returns:
            ContentResult with generated content
        """
        start_time = time.time()
        
        if not self.client:
            return ContentResult(
                content="Error: OpenAI client not available",
                generation_successful=False,
                metadata={'error': 'OpenAI client not initialized'}
            )
        
        try:
            # Generate content prompt based on type
            prompt = self._create_content_prompt(keywords_data, research_analysis, content_spec)
            
            # Generate content with OpenAI
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(content_spec)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            generated_content = response.choices[0].message.content
            word_count = len(generated_content.split())
            generation_time = time.time() - start_time
            
            # Extract citations if research papers were used
            citations = self._extract_citations_from_research(research_analysis)
            
            # Calculate quality score
            quality_score = self._calculate_content_quality(generated_content, content_spec, research_analysis)
            
            # Update statistics
            self._update_generation_stats(content_spec.content_type, generation_time, True)
            
            result = ContentResult(
                content=generated_content,
                content_type=content_spec.content_type,
                word_count=word_count,
                generation_successful=True,
                research_papers_used=len(research_analysis.get('papers_summary', [])),
                keywords_used=len(keywords_data.get('primary_keywords', [])),
                generation_time=generation_time,
                quality_score=quality_score,
                research_quality=research_analysis.get('research_quality', 'unknown'),
                citations_included=citations,
                metadata={
                    'tone': content_spec.content_tone,
                    'length': content_spec.content_length,
                    'audience': content_spec.target_audience,
                    'model_used': self.model_name,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            # Generate conceptual image if enabled (DISABLED)
            # if self.image_generation_enabled:
            #     logger.info("🎨 Generating conceptual image for content...")
            #     image_result = self.generate_conceptual_image(generated_content, content_spec.content_type, keywords_data)
            #     result.generated_image = image_result
            
            # Add external links to content
            logger.info("🔗 Adding external links to content...")
            linked_content = self.add_external_links_to_content(generated_content, keywords_data)
            result.content = linked_content
            
            logger.info(f"Content generated successfully: {word_count} words in {generation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            self._update_generation_stats(content_spec.content_type, time.time() - start_time, False)
            
            return ContentResult(
                content=f"Error generating content: {str(e)}",
                content_type=content_spec.content_type,
                generation_successful=False,
                generation_time=time.time() - start_time,
                metadata={'error': str(e)}
            )
    
    def _get_system_prompt(self, content_spec: ContentSpecification) -> str:
        """Get system prompt based on content specifications"""
        base_prompt = f"""You are an expert content creator and researcher specializing in {content_spec.content_type.replace('_', ' ')} creation. 

Your expertise includes:
- Transforming complex research into engaging, accessible content
- Writing in {content_spec.content_tone} tone for {content_spec.target_audience} audience
- Creating {content_spec.content_length} format content that drives engagement
- Integrating research findings naturally and credibly
- Optimizing content structure for readability and impact

Focus on clarity, insight, and practical value while maintaining academic credibility where appropriate."""

        # Add content-specific instructions
        if content_spec.content_type == 'blog_post':
            base_prompt += "\n\nSpecialize in SEO-optimized blog posts with clear structure, engaging headlines, and actionable insights."
        elif content_spec.content_type == 'whitepaper':
            base_prompt += "\n\nSpecialize in authoritative whitepapers with executive summaries, data analysis, and strategic recommendations."
        elif content_spec.content_type == 'social_media':
            base_prompt += "\n\nSpecialize in platform-optimized social media content with hooks, engagement tactics, and viral potential."
        
        return base_prompt
    
    def _create_content_prompt(self, 
                              keywords_data: Dict[str, Any],
                              research_analysis: Dict[str, Any],
                              content_spec: ContentSpecification) -> str:
        """Create detailed content generation prompt"""
        
        # Get template configuration
        template = self.content_templates.get(content_spec.content_type, {})
        word_range = template.get('word_ranges', {}).get(content_spec.content_length, '1000-1500 words')
        
        # Extract research data
        keywords = keywords_data.get('primary_keywords', [])[:5]
        research_summary = research_analysis.get('academic_analysis', {}).get('marketing_summary', '')
        marketing_insights = research_analysis.get('marketing_analysis', {}).get('executive_summary', '')
        papers_summary = research_analysis.get('papers_summary', [])
        
        # Format research papers
        papers_text = ""
        if papers_summary:
            papers_text = "\n".join([
                f"- '{paper['title']}' by {', '.join(paper['authors'][:2])}"
                for paper in papers_summary[:3]
            ])
        else:
            papers_text = "Content based on keyword research and best practices"
        
        # Create comprehensive prompt
        prompt = f"""
🎯 CONTENT GENERATION REQUEST

📊 RESEARCH FOUNDATION:
Primary Keywords: {', '.join(keywords)}
Research Insights: {research_summary[:400]}...
Marketing Analysis: {marketing_insights[:400]}...

📚 ACADEMIC SOURCES:
{papers_text}

🎨 CONTENT SPECIFICATIONS:
- Format: {content_spec.content_type.replace('_', ' ').title()} ({word_range})
- Tone: {content_spec.content_tone.title()}
- Audience: {content_spec.target_audience.replace('_', ' ').title()}
- Length Target: {content_spec.content_length.title()}
- Include Citations: {content_spec.include_citations}
- SEO Optimization: {content_spec.seo_optimization}

📝 SPECIAL INSTRUCTIONS:
{content_spec.additional_instructions if content_spec.additional_instructions else 'Follow best practices for the content type'}

🚀 CONTENT REQUIREMENTS:
{self._get_content_type_requirements(content_spec.content_type, content_spec.content_length)}

📈 QUALITY STANDARDS:
- Integrate research findings naturally throughout
- Maintain {content_spec.content_tone} tone consistently
- Optimize for {content_spec.target_audience} comprehension level
- Include actionable insights and practical takeaways
- Use clear structure with headings and subheadings
- Ensure content flows logically from introduction to conclusion
- Add credible citations when referencing research

Generate high-quality, engaging content that transforms the research insights into valuable, actionable information for the target audience.
"""
        
        return prompt
    
    def _get_content_type_requirements(self, content_type: str, length: str) -> str:
        """Get specific requirements for each content type"""
        
        requirements = {
            'blog_post': f"""
Create an engaging blog post with:
1. **Compelling Headline**: SEO-optimized, attention-grabbing title
2. **Hook Introduction**: Start with question, statistic, or insight (10% of content)
3. **Main Content Sections**: 3-4 sections with clear H2/H3 headings (75% of content)
4. **Actionable Takeaways**: Practical steps readers can implement (10% of content)
5. **Strong Conclusion**: Key points summary with call-to-action (5% of content)
6. **SEO Elements**: Natural keyword integration, meta description worthy intro
7. **Engagement Features**: Bullet points, numbered lists, rhetorical questions
            """,
            
            'article': f"""
Create an authoritative article with:
1. **Professional Title**: Clear, descriptive, authority-building
2. **Executive Summary**: Key findings and recommendations overview
3. **Detailed Analysis**: Multiple sections with data and insights
4. **Research Integration**: Credible citations and data points
5. **Strategic Recommendations**: Actionable business advice
6. **Conclusion**: Summary of key insights and next steps
7. **References**: Proper citation of research sources
            """,
            
            'social_media': f"""
Create platform-optimized social media content:
1. **Attention Hook**: First line must grab attention immediately
2. **Value Proposition**: Clear benefit or insight for followers
3. **Engaging Format**: Use emojis, line breaks, bullet points appropriately
4. **Call-to-Action**: Encourage likes, comments, shares, or clicks
5. **Hashtag Strategy**: Relevant, trending, and niche-specific hashtags
6. **Platform Optimization**: Format for {length} platform requirements
7. **Multiple Variants**: Provide 2-3 different approaches
            """,
            
            'marketing_copy': f"""
Create conversion-focused marketing copy:
1. **Compelling Headlines**: Multiple headline options for A/B testing
2. **Value Proposition**: Clear, unique selling proposition
3. **Benefit-Driven Content**: Focus on customer outcomes, not features
4. **Social Proof**: Integrate testimonials, statistics, credibility markers
5. **Urgency/Scarcity**: Create compelling reasons to act now
6. **Strong CTAs**: Clear, action-oriented calls-to-action
7. **Conversion Optimization**: Structure for maximum conversion potential
            """,
            
            'whitepaper': f"""
Create an authoritative whitepaper:
1. **Executive Summary**: Comprehensive overview for decision-makers
2. **Problem Statement**: Clear definition of challenges addressed
3. **Research Methodology**: Approach and data sources used
4. **Detailed Analysis**: In-depth examination of findings
5. **Case Studies**: Real-world applications and examples
6. **Strategic Recommendations**: Actionable business strategies
7. **Conclusion**: Summary and future implications
8. **Appendices**: Supporting data and additional resources
            """,
            
            'email_campaign': f"""
Create an email campaign sequence:
1. **Subject Lines**: Compelling, curiosity-driving email subjects
2. **Preview Text**: Complement subject lines with preview optimization
3. **Email Sequence**: {self.content_templates['email_campaign']['sequence_length'][length]} email series
4. **Value Progression**: Build trust and provide value before selling
5. **Personalization**: Include merge tags and segmentation suggestions
6. **CTAs**: Clear, trackable calls-to-action for each email
7. **Follow-up Strategy**: Automation and timing recommendations
            """,
            
            'press_release': f"""
Create a media-ready press release:
1. **Newsworthy Headline**: AP style, attention-grabbing announcement
2. **Compelling Lead**: Who, what, when, where, why in first paragraph
3. **Quote Integration**: Executive quotes that add value and context
4. **Supporting Details**: Background information and context
5. **Company Boilerplate**: Professional company description
6. **Contact Information**: Media contact details and availability
7. **Distribution Ready**: Format for wire services and media outlets
            """,
            
            'case_study': f"""
Create a compelling case study:
1. **Executive Summary**: Key outcomes and success metrics overview
2. **Challenge Definition**: Specific problems faced by the client
3. **Solution Description**: Detailed approach and implementation
4. **Results & Metrics**: Quantifiable outcomes and ROI data
5. **Client Testimonials**: Authentic quotes from stakeholders
6. **Lessons Learned**: Insights applicable to similar situations
7. **Next Steps**: How readers can achieve similar results
            """
        }
        
        return requirements.get(content_type, "Create high-quality content following best practices for the specified format.")
    
    def _extract_citations_from_research(self, research_analysis: Dict[str, Any]) -> List[str]:
        """Extract citation information from research analysis"""
        citations = []
        
        papers_summary = research_analysis.get('papers_summary', [])
        for paper in papers_summary:
            if paper.get('title') and paper.get('authors'):
                citation = f"{paper['title']} - {', '.join(paper['authors'][:2])}"
                citations.append(citation)
        
        return citations
    
    def _calculate_content_quality(self, 
                                  content: str, 
                                  content_spec: ContentSpecification,
                                  research_analysis: Dict[str, Any]) -> float:
        """Calculate a quality score for the generated content"""
        score = 0.0
        
        # Word count appropriateness (20% of score)
        word_count = len(content.split())
        target_ranges = {
            'short': (800, 1500),
            'medium': (1200, 2500),
            'long': (2000, 4000)
        }
        
        target_min, target_max = target_ranges.get(content_spec.content_length, (1000, 2000))
        if target_min <= word_count <= target_max:
            score += 0.2
        elif word_count >= target_min * 0.8 and word_count <= target_max * 1.2:
            score += 0.15
        else:
            score += 0.1
        
        # Structure quality (30% of score)
        has_headings = bool(re.search(r'#+\s+', content) or re.search(r'^[A-Z][^.]*:$', content, re.MULTILINE))
        has_lists = bool(re.search(r'^\s*[-*•]\s+', content, re.MULTILINE) or re.search(r'^\s*\d+\.\s+', content, re.MULTILINE))
        has_paragraphs = len(content.split('\n\n')) >= 3
        
        structure_score = (has_headings * 0.1) + (has_lists * 0.1) + (has_paragraphs * 0.1)
        score += structure_score
        
        # Research integration (25% of score)
        papers_count = len(research_analysis.get('papers_summary', []))
        if papers_count >= 3:
            score += 0.25
        elif papers_count >= 1:
            score += 0.15
        else:
            score += 0.05
        
        # Content richness (25% of score)
        sentences = content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0
        
        if 15 <= avg_sentence_length <= 25:  # Optimal readability
            score += 0.15
        else:
            score += 0.1
        
        # Vocabulary diversity
        words = content.lower().split()
        unique_words = len(set(words))
        diversity_ratio = unique_words / len(words) if words else 0
        
        if diversity_ratio >= 0.6:
            score += 0.1
        elif diversity_ratio >= 0.4:
            score += 0.05
        
        return min(score, 1.0)  # Cap at 1.0
    
    # def extract_visual_concept_from_content(self, content: str, keywords_data: Dict[str, Any]) -> str:
    #     """Extract key visual concepts from generated content for image generation"""
    #     
    #     # Extract primary keywords for visual concepts
    #     primary_keywords = keywords_data.get('primary_keywords', [])[:3]
    #     
    #     # Look for key concepts in the content
    #     concept_indicators = [
    #         'strategy', 'framework', 'process', 'system', 'growth', 'transformation',
    #         'innovation', 'optimization', 'analysis', 'methodology', 'approach',
    #         'solution', 'implementation', 'performance', 'efficiency', 'success'
    #     ]
    #     
    #     # Find the most relevant concepts
    #     content_lower = content.lower()
    #     found_concepts = [concept for concept in concept_indicators if concept in content_lower]
    #     
    #     # Create a conceptual description
    #     if primary_keywords and found_concepts:
    #         main_keyword = primary_keywords[0]
    #         main_concept = found_concepts[0] if found_concepts else 'strategy'
    #         
    #         return f"{main_keyword} {main_concept}"
    #     elif primary_keywords:
    #         return primary_keywords[0]
    #     else:
    #         return "business strategy concept"
    
    # def create_minimalistic_image_prompt(self, visual_concept: str, content_type: str) -> str:
    #     """Create an optimized prompt for minimalistic conceptual images"""
    #     
    #     # Base style elements for minimalistic design
    #     base_style = "minimalistic, clean, professional, conceptual"
    #     
    #     # Content type specific visual elements
    #     content_visual_elements = {
    #         'blog_post': 'editorial illustration, thought leadership visual',
    #         'article': 'analytical diagram, research visualization', 
    #         'b2b_blog_package': 'corporate infographic, business strategy visual',
    #         'b2b_linkedin_post': 'social media graphic, professional insight visual',
    #         'whitepaper': 'technical diagram, authoritative visualization',
    #         'case_study': 'success story visual, results infographic',
    #         'marketing_copy': 'conversion-focused graphic, persuasive visual'
    #     }
    #     
    #     visual_elements = content_visual_elements.get(content_type, 'business concept illustration')
    #     
    #     # Create the optimized prompt
    #     prompt = f"""
    #     Create a {base_style} illustration representing {visual_concept}.
    #     Style: {visual_elements}, geometric shapes, subtle gradients, limited color palette.
    #     Design elements: Clean lines, negative space, abstract symbols, modern typography hints.
    #     Color scheme: Professional blues and grays with subtle accent colors.
    #     Composition: Centered, balanced, uncluttered, suitable for business presentations.
    #     Avoid: Realistic photos, complex details, busy backgrounds, multiple focal points.
    #     Focus: Single clear concept, visual metaphor, business-appropriate aesthetic.
    #     """
    #     
    #     return prompt.strip()
    
    # def generate_conceptual_image(self, content: str, content_type: str, keywords_data: Dict[str, Any]) -> ImageGenerationResult:
    #     """Generate a conceptual minimalistic image based on content"""
    #     
    #     start_time = time.time()
    #     result = ImageGenerationResult()
    #     
    #     if not self.client or not self.image_generation_enabled:
    #         result.error_message = "Image generation not available"
    #         return result
    #     
    #     try:
    #         logger.info("🎨 Starting conceptual image generation...")
    #         
    #         # Extract visual concept from content
    #         visual_concept = self.extract_visual_concept_from_content(content, keywords_data)
    #         result.concept_extracted = visual_concept
    #         
    #         # Create optimized minimalistic prompt
    #         image_prompt = self.create_minimalistic_image_prompt(visual_concept, content_type)
    #         result.image_prompt = image_prompt
    #         
    #         logger.info(f"🎨 Generating image for concept: {visual_concept}")
    #         
    #         # Generate image with OpenAI DALL-E
    #         response = self.client.images.generate(
    #             model=self.image_model,
    #             prompt=image_prompt,
    #             size=self.image_size,
    #             quality=self.image_quality,
    #             n=1
    #         )
    #         
    #         if response.data and len(response.data) > 0:
    #             result.image_url = response.data[0].url
    #             result.generation_successful = True
    #             result.generation_time = time.time() - start_time
    #             result.image_style = "minimalistic"
    #             
    #             # Download and save the image
    #             image_filename = self._download_and_save_image(result.image_url, visual_concept)
    #             result.image_filename = image_filename
    #             
    #             # Update statistics
    #             self.generation_stats['images_generated'] += 1
    #             self.generation_stats['successful_image_generations'] += 1
    #             
    #             logger.info(f"✅ Image generated successfully in {result.generation_time:.2f}s")
    #             logger.info(f"🖼️ Image saved as: {image_filename}")
    #             
    #         else:
    #             result.error_message = "No image data received from OpenAI"
    #             
    #     except Exception as e:
    #         result.error_message = str(e)
    #         result.generation_time = time.time() - start_time
    #         logger.error(f"❌ Image generation failed: {e}")
    #     
    #     result.metadata = {
    #         'model_used': self.image_model,
    #         'size': self.image_size,
    #         'quality': self.image_quality,
    #         'timestamp': datetime.now().isoformat()
    #     }
    #     
    #     return result
    
    def add_external_links_to_content(self, content: str, keywords_data: Dict[str, Any]) -> str:
        """Add 2 external links with optimized anchor phrases, avoiding intro and conclusion"""
        
        try:
            # Define high-authority external resources with relevant anchor phrases
            external_resources = [
                {
                    'url': 'https://www.gartner.com/en/research',
                    'anchor_phrases': ['industry research', 'market analysis', 'technology trends', 'digital transformation insights', 'business intelligence reports']
                },
                {
                    'url': 'https://www.mckinsey.com/featured-insights',
                    'anchor_phrases': ['strategic insights', 'business strategy', 'operational excellence', 'management consulting', 'industry best practices']
                },
                {
                    'url': 'https://hbr.org/topic/strategy',
                    'anchor_phrases': ['strategic planning', 'business leadership', 'organizational strategy', 'competitive advantage', 'strategic thinking']
                },
                {
                    'url': 'https://www.forrester.com/research',
                    'anchor_phrases': ['customer experience', 'technology research', 'market forecasts', 'business transformation', 'digital strategy']
                },
                {
                    'url': 'https://www2.deloitte.com/us/en/insights.html',
                    'anchor_phrases': ['business insights', 'industry analysis', 'emerging trends', 'digital innovation', 'strategic consulting']
                }
            ]
            
            # Split content into paragraphs
            paragraphs = content.split('\n\n')
            
            if len(paragraphs) < 4:
                # Content too short, return as is
                return content
            
            # Avoid first and last paragraphs (intro/conclusion)
            middle_paragraphs = paragraphs[1:-1]
            
            if len(middle_paragraphs) < 2:
                # Not enough middle content
                return content
            
            # Extract primary keywords for context
            primary_keywords = keywords_data.get('primary_keywords', [])
            
            # Select 2 resources and anchor phrases
            import random
            selected_resources = random.sample(external_resources, min(2, len(external_resources)))
            
            links_added = 0
            modified_paragraphs = paragraphs.copy()
            
            for i, resource in enumerate(selected_resources):
                if links_added >= 2:
                    break
                
                # Choose anchor phrase based on content context
                anchor_phrase = self._select_best_anchor_phrase(resource['anchor_phrases'], primary_keywords, content)
                
                # Find a good position in middle paragraphs
                target_paragraph_idx = 1 + (i * len(middle_paragraphs) // 2)
                
                if target_paragraph_idx < len(modified_paragraphs) - 1:
                    # Insert link naturally into the paragraph
                    original_paragraph = modified_paragraphs[target_paragraph_idx]
                    modified_paragraph = self._insert_link_naturally(original_paragraph, resource['url'], anchor_phrase)
                    
                    if modified_paragraph != original_paragraph:
                        modified_paragraphs[target_paragraph_idx] = modified_paragraph
                        links_added += 1
            
            logger.info(f"🔗 Added {links_added} external links to content")
            return '\n\n'.join(modified_paragraphs)
            
        except Exception as e:
            logger.error(f"❌ Failed to add external links: {e}")
            return content
    
    def _select_best_anchor_phrase(self, anchor_phrases: List[str], keywords: List[str], content: str) -> str:
        """Select the most contextually relevant anchor phrase"""
        
        content_lower = content.lower()
        
        # Score anchor phrases based on keyword and content relevance
        scored_phrases = []
        for phrase in anchor_phrases:
            score = 0
            phrase_words = phrase.lower().split()
            
            # Check if phrase words appear in keywords
            for word in phrase_words:
                if any(word in keyword.lower() for keyword in keywords):
                    score += 2
                
                # Check if phrase words appear in content
                if word in content_lower:
                    score += 1
            
            scored_phrases.append((phrase, score))
        
        # Return highest scoring phrase, or first if all score 0
        best_phrase = max(scored_phrases, key=lambda x: x[1])
        return best_phrase[0] if best_phrase[1] > 0 else anchor_phrases[0]
    
    def _insert_link_naturally(self, paragraph: str, url: str, anchor_phrase: str) -> str:
        """Insert link naturally into a paragraph"""
        
        # Look for natural insertion points
        sentences = paragraph.split('. ')
        
        if len(sentences) < 2:
            return paragraph
        
        # Try to find a sentence where the link would fit naturally
        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()
            
            # Look for contextual cues where a link would be natural
            link_cues = [
                'research shows', 'studies indicate', 'according to', 'experts suggest',
                'industry leaders', 'best practices', 'proven strategies', 'analysis reveals'
            ]
            
            if any(cue in sentence_lower for cue in link_cues):
                # Insert link at the end of this sentence
                if not sentence.endswith('.'):
                    sentence += '.'
                
                linked_sentence = f"{sentence} This aligns with findings from <a href='{url}' target='_blank' rel='noopener'>{anchor_phrase}</a>."
                sentences[i] = linked_sentence
                return '. '.join(sentences)
        
        # If no natural insertion point found, add to the middle sentence
        middle_idx = len(sentences) // 2
        middle_sentence = sentences[middle_idx]
        
        if not middle_sentence.endswith('.'):
            middle_sentence += '.'
        
        # Add link as a supporting reference
        linked_sentence = f"{middle_sentence} For more insights on this topic, see <a href='{url}' target='_blank' rel='noopener'>{anchor_phrase}</a>."
        sentences[middle_idx] = linked_sentence
        
        return '. '.join(sentences)

    # def _download_and_save_image(self, image_url: str, concept: str) -> str:
    #     """Download and save the generated image locally"""
    #     
    #     try:
    #         # Create images directory if it doesn't exist
    #         images_dir = "generated_images"
    #         os.makedirs(images_dir, exist_ok=True)
    #         
    #         # Create filename based on concept and timestamp
    #         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    #         safe_concept = re.sub(r'[^\w\s-]', '', concept).strip()[:30]
    #         safe_concept = re.sub(r'[-\s]+', '_', safe_concept)
    #         filename = f"concept_{safe_concept}_{timestamp}.png"
    #         filepath = os.path.join(images_dir, filename)
    #         
    #         # Download the image
    #         response = requests.get(image_url, timeout=30)
    #         response.raise_for_status()
    #         
    #         # Save the image
    #         with open(filepath, 'wb') as f:
    #             f.write(response.content)
    #         
    #         logger.info(f"💾 Image saved locally: {filepath}")
    #         return filepath
    #         
    #     except Exception as e:
    #         logger.error(f"❌ Failed to download/save image: {e}")
    #         return ""

    def _update_generation_stats(self, content_type: str, generation_time: float, success: bool):
        """Update generation statistics"""
        self.generation_stats['total_generated'] += 1
        
        if success:
            self.generation_stats['successful_generations'] += 1
        
        # Update average generation time
        current_avg = self.generation_stats['average_generation_time']
        total = self.generation_stats['total_generated']
        self.generation_stats['average_generation_time'] = (
            (current_avg * (total - 1) + generation_time) / total
        )
        
        # Update content type stats
        if content_type not in self.generation_stats['content_types_generated']:
            self.generation_stats['content_types_generated'][content_type] = 0
        self.generation_stats['content_types_generated'][content_type] += 1
    
    def create_comprehensive_document(self, 
                                    content_result: ContentResult,
                                    keywords_data: Dict[str, Any],
                                    research_analysis: Dict[str, Any],
                                    content_spec: ContentSpecification) -> Dict[str, Any]:
        """
        Create a comprehensive Word document with the generated content
        
        Args:
            content_result: Generated content result
            keywords_data: Keywords data
            research_analysis: Research analysis results
            content_spec: Content specifications
            
        Returns:
            Dictionary with document creation results
        """
        if not DOC_CREATION_AVAILABLE:
            return {
                'success': False,
                'error': 'Document creation libraries not available'
            }
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_content_{content_spec.content_type}_{timestamp}.docx"
            
            # Create Word document
            doc = Document()
            
            # Title page
            self._create_title_page(doc, content_spec, content_result)
            
            # Executive summary page
            self._create_executive_summary(doc, content_result, research_analysis)
            
            # Content metadata
            self._create_content_metadata(doc, content_spec, content_result, keywords_data)
            
            # Main content
            self._create_main_content(doc, content_result)
            
            # Research appendix
            if research_analysis.get('papers_summary'):
                self._create_research_appendix(doc, research_analysis, keywords_data)
            
            # Generation details
            self._create_generation_details(doc, content_result, self.generation_stats)
            
            # Save document
            doc.save(filename)
            
            file_size = os.path.getsize(filename) if os.path.exists(filename) else 0
            
            logger.info(f"Comprehensive document created: {filename} ({file_size} bytes)")
            
            return {
                'success': True,
                'filename': filename,
                'file_size': file_size,
                'word_count': content_result.word_count,
                'pages_estimated': max(1, content_result.word_count // 300),
                'creation_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Document creation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_title_page(self, doc: Document, content_spec: ContentSpecification, content_result: ContentResult):
        """Create professional title page"""
        # Main title
        title = doc.add_heading(f'{content_spec.content_type.replace("_", " ").title()}', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Subtitle
        subtitle = doc.add_paragraph('AI-Generated Research-Driven Content')
        subtitle_format = subtitle.runs[0]
        subtitle_format.font.size = 14
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Add space
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Generation info
        info_para = doc.add_paragraph(f'Generated on {datetime.now().strftime("%B %d, %Y")}')
        info_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        quality_para = doc.add_paragraph(f'Content Quality Score: {content_result.quality_score:.1%}')
        quality_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_page_break()
    
    def _create_executive_summary(self, doc: Document, content_result: ContentResult, research_analysis: Dict[str, Any]):
        """Create executive summary section"""
        doc.add_heading('Executive Summary', level=1)
        
        # Content overview
        summary_text = f"""
This document presents AI-generated content based on comprehensive research analysis. 
The content incorporates findings from {content_result.research_papers_used} research papers 
and {content_result.keywords_used} primary keywords.

Key Metrics:
• Word Count: {content_result.word_count:,} words
• Generation Time: {content_result.generation_time:.1f} seconds
• Research Quality: {content_result.research_quality.title()}
• Quality Score: {content_result.quality_score:.1%}

Research Foundation:
{research_analysis.get('academic_analysis', {}).get('marketing_summary', 'Content generated using advanced keyword analysis and best practices.')[:300]}...
        """
        
        doc.add_paragraph(summary_text.strip())
        doc.add_page_break()
    
    def _create_content_metadata(self, doc: Document, content_spec: ContentSpecification, 
                                content_result: ContentResult, keywords_data: Dict[str, Any]):
        """Create content metadata section"""
        doc.add_heading('Content Specifications', level=1)
        
        # Create metadata table
        table = doc.add_table(rows=8, cols=2)
        table.style = 'Table Grid'
        
        metadata_rows = [
            ('Content Type', content_spec.content_type.replace('_', ' ').title()),
            ('Tone & Style', content_spec.content_tone.title()),
            ('Target Length', content_spec.content_length.title()),
            ('Target Audience', content_spec.target_audience.replace('_', ' ').title()),
            ('Actual Word Count', f'{content_result.word_count:,} words'),
            ('Research Papers Used', str(content_result.research_papers_used)),
            ('Keywords Incorporated', str(content_result.keywords_used)),
            ('AI Model Used', content_result.metadata.get('model_used', 'GPT-4'))
        ]
        
        for i, (label, value) in enumerate(metadata_rows):
            row_cells = table.rows[i].cells
            row_cells[0].text = label
            row_cells[1].text = value
            row_cells[0].paragraphs[0].runs[0].bold = True
        
        # Keywords section
        doc.add_heading('Primary Keywords Used', level=2)
        keywords = keywords_data.get('primary_keywords', [])
        for keyword in keywords[:10]:
            doc.add_paragraph(f'• {keyword}', style='List Bullet')
        
        # Research topics
        research_topics = keywords_data.get('research_topics', [])
        if research_topics:
            doc.add_heading('Research Topics', level=2)
            for topic in research_topics[:5]:
                doc.add_paragraph(f'• {topic}', style='List Bullet')
        
        doc.add_page_break()
    
    def _create_main_content(self, doc: Document, content_result: ContentResult):
        """Create main content section"""
        doc.add_heading('Generated Content', level=1)
        
        content_text = content_result.content
        
        # Process content for better formatting
        sections = content_text.split('\n\n')
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Check if it's a header
            if (section.startswith('#') or 
                (len(section) < 100 and (section.isupper() or section.endswith(':')))):
                
                # Remove markdown formatting and create heading
                header_text = section.replace('#', '').strip()
                if header_text.endswith(':'):
                    header_text = header_text[:-1]
                doc.add_heading(header_text, level=2)
            else:
                # Regular paragraph
                doc.add_paragraph(section)
        
        doc.add_page_break()
    
    def _create_research_appendix(self, doc: Document, research_analysis: Dict[str, Any], keywords_data: Dict[str, Any]):
        """Create research appendix section"""
        doc.add_heading('Research Foundation', level=1)
        
        # Academic analysis summary
        academic_summary = research_analysis.get('academic_analysis', {}).get('marketing_summary', '')
        if academic_summary:
            doc.add_heading('Research Analysis', level=2)
            doc.add_paragraph(academic_summary)
        
        # Research papers used
        papers_summary = research_analysis.get('papers_summary', [])
        if papers_summary:
            doc.add_heading('Research Papers Referenced', level=2)
            
            for i, paper in enumerate(papers_summary, 1):
                paper_para = doc.add_paragraph(f"{i}. ")
                paper_para.add_run(paper['title']).bold = True
                paper_para.add_run(f"\nAuthors: {', '.join(paper['authors'])}")
                paper_para.add_run(f"\nCitations: {paper.get('citations', 'N/A')}")
                if paper.get('business_relevance'):
                    paper_para.add_run(f"\nBusiness Relevance: {paper['business_relevance']}")
                paper_para.add_run("\n")
        
        # Marketing analysis
        marketing_summary = research_analysis.get('marketing_analysis', {}).get('executive_summary', '')
        if marketing_summary:
            doc.add_heading('Marketing Analysis', level=2)
            doc.add_paragraph(marketing_summary)
        
        doc.add_page_break()
    
    def _create_generation_details(self, doc: Document, content_result: ContentResult, generation_stats: Dict[str, Any]):
        """Create generation details section"""
        doc.add_heading('Content Generation Details', level=1)
        
        details_text = f"""
This content was generated using advanced AI technology combined with comprehensive research analysis.

Generation Process:
1. Keyword extraction from source document
2. Academic research paper discovery and analysis
3. Research synthesis and insight extraction
4. AI content generation with research integration
5. Quality assessment and optimization

Performance Metrics:
• Generation Time: {content_result.generation_time:.2f} seconds
• Content Quality Score: {content_result.quality_score:.1%}
• Research Integration: {content_result.research_papers_used} papers utilized
• Keyword Incorporation: {content_result.keywords_used} primary keywords

Technical Details:
• AI Model: {content_result.metadata.get('model_used', 'GPT-4')}
• Research Quality: {content_result.research_quality.title()}
• Citations Included: {len(content_result.citations_included)}
• Generation Timestamp: {content_result.metadata.get('timestamp', 'N/A')}

System Statistics:
• Total Content Generated: {generation_stats.get('total_generated', 0)}
• Success Rate: {(generation_stats.get('successful_generations', 0) / max(1, generation_stats.get('total_generated', 1)) * 100):.1f}%
• Average Generation Time: {generation_stats.get('average_generation_time', 0):.1f} seconds
        """
        
        doc.add_paragraph(details_text.strip())
    
    def run_complete_content_pipeline(self, 
                                    google_file_id: str,
                                    content_spec: ContentSpecification,
                                    max_papers: int = 10) -> Dict[str, Any]:
        """
        Run the complete content generation pipeline
        
        Args:
            google_file_id: Google file ID for keyword extraction
            content_spec: Content generation specifications
            max_papers: Maximum number of research papers to use
            
        Returns:
            Complete pipeline results
        """
        pipeline_start = time.time()
        
        try:
            logger.info(f"🚀 Starting complete content pipeline for {content_spec.content_type}")
            
            # Step 1: Extract keywords
            logger.info("📝 Step 1: Extracting keywords from Google file")
            keywords_data = self.extract_keywords_from_google_file(google_file_id)
            
            # Step 2: Conduct research
            logger.info("🔍 Step 2: Conducting research based on keywords")
            papers = self.conduct_research(keywords_data, max_papers)
            
            # Step 3: Analyze research
            logger.info("📊 Step 3: Analyzing research for content generation")
            research_analysis = self.analyze_research_for_content(papers, keywords_data)
            
            # Step 4: Generate content
            logger.info("✨ Step 4: Generating AI content")
            content_result = self.generate_content(keywords_data, research_analysis, content_spec)
            
            # Step 5: Create document
            logger.info("📄 Step 5: Creating comprehensive document")
            document_result = self.create_comprehensive_document(
                content_result, keywords_data, research_analysis, content_spec
            )
            
            pipeline_time = time.time() - pipeline_start
            
            logger.info(f"✅ Content pipeline completed in {pipeline_time:.2f}s")
            
            return {
                'success': True,
                'content_result': content_result,
                'document_result': document_result,
                'research_summary': {
                    'keywords_extracted': len(keywords_data.get('primary_keywords', [])),
                    'papers_found': len(papers),
                    'research_quality': research_analysis.get('research_quality', 'unknown')
                },
                'pipeline_time': pipeline_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Content pipeline failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'pipeline_time': time.time() - pipeline_start
            }
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get current generation statistics"""
        return {
            **self.generation_stats,
            'system_status': {
                'openai_available': self.client is not None,
                'research_agent_available': self.research_agent is not None,
                'document_creation_available': DOC_CREATION_AVAILABLE
            },
            'content_templates_loaded': len(self.content_templates),
            'timestamp': datetime.now().isoformat()
        }

# Example usage
if __name__ == "__main__":
    # Initialize the agent
    agent = AIContentResearchAgent()
    
    # Example content specification
    content_spec = ContentSpecification(
        content_type="blog_post",
        content_tone="professional",
        content_length="medium",
        target_audience="business_professionals",
        additional_instructions="Focus on practical implementation strategies"
    )
    
    # Test the system
    print("🧪 Testing AI Content Research Agent")
    stats = agent.get_generation_statistics()
    print(f"System Status: {stats['system_status']}")
    
    # Example pipeline run (uncomment to test with actual Google file)
    # result = agent.run_complete_content_pipeline("your-google-file-id", content_spec)
    # print(f"Pipeline Result: {result['success']}") 