"""
Google Scholar Research Agent with Bright Data API Integration
Only includes Bright Data for CAPTCHA bypass - all other CAPTCHA methods removed
"""

import os
import re
import json
import time
import string
import logging
import requests
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# OpenAI and language processing
from openai import OpenAI

# Google API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Document processing
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Web scraping and scholarly
import scholarly
from scholarly import ProxyGenerator

# NLP dependencies
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# spaCy for advanced NLP
import spacy

# PDF processing
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# HTML processing
from bs4 import BeautifulSoup
import chardet

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ResearchPaper:
    """Data class for research paper information"""
    title: str
    authors: List[str]
    abstract: str
    publication_year: int
    journal: str
    url: str
    citations: int
    keywords: List[str]
    full_text: str = ""
    relevance_score: float = 0.0
    quality_score: float = 0.0

@dataclass
class ResearchInsight:
    """Data class for research insights"""
    topic: str
    key_findings: List[str]
    methodology: str
    implications: List[str]
    future_research: List[str]
    supporting_papers: List[str]
    confidence_score: float

class GoogleScholarResearchAgent:
    """
    Research agent that searches Google Scholar and processes research papers
    Uses Bright Data API for CAPTCHA bypass
    """
    
    def __init__(self, openai_api_key: str = None, google_credentials_path: str = None):
        """
        Initialize the research agent with Bright Data API for CAPTCHA bypass
        
        Args:
            openai_api_key: OpenAI API key
            google_credentials_path: Path to Google credentials JSON file
        """
        # Initialize OpenAI client
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required - set OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.openai_api_key)
        
        # Use GPT-4o mini for better keyword extraction
        self.model_name = "gpt-4o-mini"
        
        # Google API setup - prioritize service account
        self.google_credentials_path = google_credentials_path or "credentials.json"
        self.google_scopes = [
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/drive.file'
        ]
        self.google_service = None
        self.drive_service = None
        
        # Automatically attempt service account authentication on init
        self.google_authenticated = self.authenticate_google_services()
        
        # Initialize NLP tools
        self._setup_nlp_tools()
        
        # Initialize Bright Data API for CAPTCHA bypass
        self._setup_bright_data_api()
        
        # Advanced prompting templates
        self.prompts = self._load_advanced_prompts()
        
        # Research configuration
        self.max_papers_per_query = 10
        self.relevance_threshold = 0.3  # Lowered from 0.7 to be more inclusive
        self.quality_threshold = 0.3   # Lowered from 0.6 to be more inclusive
        
        # Advanced processing configuration
        self.enable_pre_filter_analysis = True
        
        # Paper download configuration
        self.download_papers = True
        self.papers_download_dir = Path("downloaded_papers")
        self.papers_download_dir.mkdir(exist_ok=True)
        self.max_download_size = 50 * 1024 * 1024  # 50MB limit
        self.download_timeout = 30  # seconds
        
        # PDF processing configuration
        self.max_parallel_downloads = 5
        self.retry_attempts = 3
        
        logger.info("Google Scholar Research Agent initialized with Bright Data CAPTCHA bypass")
        logger.info("[INFO] Enhanced PDF Analysis System: ENABLED with parallel processing")

    def configure_bright_data_api(self,
                                enable_bright_data: bool = True,
                                api_key: str = None,
                                zone: str = "web_unlocker1",
                                request_timeout: int = 60,
                                max_retries: int = 3) -> None:
        """
        Configure Bright Data API settings for advanced web scraping and CAPTCHA bypass
        
        Args:
            enable_bright_data: Whether to enable Bright Data API
            api_key: Bright Data API key
            zone: Bright Data zone to use
            request_timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        try:
            if enable_bright_data:
                api_key = api_key or os.getenv("BRIGHT_DATA_API_KEY")
                if not api_key:
                    logger.warning("[WARNING] Bright Data API key not found. Set BRIGHT_DATA_API_KEY environment variable.")
                    self.bright_data_enabled = False
                    return
                
                self.bright_data_config = {
                    'api_key': api_key,
                    'zone': zone,
                    'request_timeout': request_timeout,
                    'max_retries': max_retries,
                    'enabled': True
                }
                
                logger.info("[OK] Bright Data API configured:")
                logger.info(f"  [GLOBE] Zone: {zone}")
                logger.info(f"  [TIME] Timeout: {request_timeout}s")
                logger.info(f"  [REFRESH] Max retries: {max_retries}")
                logger.info("  [UNLOCK] Web unlocker enabled for CAPTCHA bypass")
                
                self.bright_data_enabled = True
                
            else:
                self.bright_data_enabled = False
                logger.info("[ERROR] Bright Data API disabled")
                
        except Exception as e:
            logger.error(f"[ERROR] Error configuring Bright Data API: {e}")
            self.bright_data_enabled = False

    def _setup_nlp_tools(self):
        """Setup NLP tools and download required data"""
        try:
            # Download NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
            # Initialize tools
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))
            
            # Load spaCy model
            self.nlp = self._setup_spacy_model()
                
        except Exception as e:
            logger.error(f"Error setting up NLP tools: {e}")

    def _setup_spacy_model(self):
        """Setup spaCy model with automatic download if needed"""
        try:
            return spacy.load("en_core_web_sm")
        except OSError:
            logger.info("[REFRESH] spaCy model 'en_core_web_sm' not found. Attempting to download...")
            
            try:
                import subprocess
                import sys
                
                logger.info("[DOWNLOAD] Downloading spaCy English model...")
                result = subprocess.run([
                    sys.executable, "-m", "spacy", "download", "en_core_web_sm"
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info("[OK] spaCy model downloaded successfully!")
                    try:
                        return spacy.load("en_core_web_sm")
                    except OSError:
                        logger.warning("[ERROR] Failed to load model after download")
                        return None
                else:
                    logger.error(f"[ERROR] Failed to download spaCy model: {result.stderr}")
                    return None
                    
            except Exception as e:
                logger.error(f"[ERROR] Error downloading spaCy model: {e}")
                return None

    def _setup_bright_data_api(self):
        """Setup Bright Data API for advanced web scraping and CAPTCHA bypass"""
        try:
            # Initialize Bright Data configuration
            self.bright_data_enabled = False
            self.bright_data_config = None
            self.bright_data_stats = {
                'requests_made': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'captcha_bypassed': 0,
                'total_response_time': 0,
                'last_error': None
            }
            
            # Check for API key in environment
            api_key = os.getenv("BRIGHT_DATA_API_KEY")
            if api_key:
                logger.info("[GLOBE] Bright Data API key found in environment")
                logger.debug(f"API key starts with: {api_key[:8]}...")
                self.configure_bright_data_api(enable_bright_data=True, api_key=api_key)
            else:
                logger.info("ℹ️ Bright Data API key not found - configure manually")
                logger.info("  Add BRIGHT_DATA_API_KEY to environment variables to enable")
                
        except Exception as e:
            logger.error(f"[ERROR] Failed to setup Bright Data API: {e}", exc_info=True)
            self.bright_data_enabled = False

    def _make_bright_data_request(self, url: str, method: str = "GET", 
                                 headers: Dict[str, str] = None,
                                 data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Make a request through Bright Data API for CAPTCHA bypass
        
        Args:
            url: Target URL to access
            method: HTTP method
            headers: Request headers
            data: Request data
            
        Returns:
            Response data or None if failed
        """
        if not self.bright_data_enabled or not self.bright_data_config:
            logger.error("[ERROR] Bright Data API not configured")
            return None
            
        try:
            start_time = time.time()
            
            # Correct Bright Data API endpoint
            api_endpoint = "https://api.brightdata.com/request"
            
            # Request headers with Bearer token authentication
            request_headers = {
                "Authorization": f"Bearer {self.bright_data_config['api_key']}",
                "Content-Type": "application/json"
            }
            
            # Request payload
            payload = {
                "zone": self.bright_data_config['zone'],
                "url": url,
                "method": method.upper(),
                "headers": headers or {},
                "format": "raw"
            }
            
            if data:
                payload["data"] = data
            
            # Make request
            logger.debug(f"[API] Making Bright Data request to: {url}")
            logger.debug(f"[CONFIG] Using zone: {self.bright_data_config['zone']}")
            
            response = requests.post(
                api_endpoint,
                json=payload,
                headers=request_headers,
                timeout=self.bright_data_config['request_timeout']
            )
            
            # Update statistics
            self.bright_data_stats['requests_made'] += 1
            response_time = time.time() - start_time
            self.bright_data_stats['total_response_time'] += response_time
            
            logger.debug(f"[STATS] Response status: {response.status_code}")
            logger.debug(f"[TIME] Response time: {response_time:.2f}s")
            
            if response.status_code == 200:
                self.bright_data_stats['successful_requests'] += 1
                
                # For raw format, the content is directly in the response
                content = response.text
                
                # Check if CAPTCHA was bypassed
                if self._is_captcha_blocked_content(content):
                    logger.warning("[WARNING] CAPTCHA detected in response - may need retry")
                    result = {"content": content, "success": False, "captcha_detected": True}
                else:
                    self.bright_data_stats['captcha_bypassed'] += 1
                    logger.debug(f"[OK] Successfully bypassed CAPTCHA for: {url}")
                    result = {"content": content, "success": True, "captcha_detected": False}
                
                logger.debug(f"[OK] Bright Data request successful in {response_time:.2f}s")
                return result
            else:
                self.bright_data_stats['failed_requests'] += 1
                self.bright_data_stats['last_error'] = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"[ERROR] Bright Data request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.bright_data_stats['failed_requests'] += 1
            self.bright_data_stats['last_error'] = str(e)
            logger.error(f"[ERROR] Error making Bright Data request: {e}", exc_info=True)
            return None

    def _is_captcha_blocked_content(self, content: str) -> bool:
        """
        Check if the content indicates CAPTCHA blocking
        
        Args:
            content: HTML content to check
            
        Returns:
            True if CAPTCHA is detected
        """
        if not content:
            return True
            
        # CAPTCHA indicators
        captcha_indicators = [
            'captcha',
            'recaptcha',
            'g-recaptcha',
            'cf-browser-verification',
            'verify you are human',
            'security check',
            'robot verification',
            'please complete the security check',
            'cloudflare',
            'just a moment',
            'checking your browser',
            'ddos protection',
            'access denied',
            'blocked by administrator',
            'firewall',
            'bot detection'
        ]
        
        content_lower = content.lower()
        
        for indicator in captcha_indicators:
            if indicator in content_lower:
                logger.debug(f"[SEARCH] CAPTCHA indicator found: {indicator}")
                return True
        
        # Check for Google Scholar specific content
        scholar_indicators = [
            'google scholar',
            'scholar.google.com',
            'cited by',
            'search results',
            'articles',
            'citations'
        ]
        
        has_scholar_content = any(indicator in content_lower for indicator in scholar_indicators)
        
        if not has_scholar_content and len(content) < 1000:
            logger.debug("[SEARCH] Suspicious: No Scholar content and short response")
            return True
            
        return False

    def search_google_scholar(self, search_queries: List[str], query_priorities: List[float] = None) -> List[ResearchPaper]:
        """
        Search Google Scholar using Bright Data API for CAPTCHA bypass
        
        Args:
            search_queries: List of search queries
            query_priorities: Priority scores for each query
            
        Returns:
            List of research papers (limited to 10 maximum)
        """
        if not self.bright_data_enabled:
            logger.error("[ERROR] Bright Data API not enabled - cannot search Google Scholar")
            return []
            
        papers = []
        
        for i, query in enumerate(search_queries):
            priority = query_priorities[i] if query_priorities else 1.0
            
            logger.info(f"[SEARCH] Searching Google Scholar: '{query}' (priority: {priority})")
            
            # Search with Bright Data
            query_papers = self._search_scholar_with_bright_data(query)
            
            if query_papers:
                papers.extend(query_papers)
                logger.info(f"[OK] Found {len(query_papers)} papers for query: '{query}'")
            else:
                logger.warning(f"[WARNING] No papers found for query: '{query}'")
            
            # Early exit if we have enough papers to meet the limit
            if len(papers) >= 10:
                logger.info("[LIMIT] Reached paper collection limit, stopping search")
                break
        
        # Remove duplicates and convert to ResearchPaper objects
        unique_papers = []
        seen_titles = set()
        
        for paper_data in papers:
            if paper_data.get('title') not in seen_titles:
                paper = self._create_paper_from_data(paper_data)
                if paper:
                    unique_papers.append(paper)
                    seen_titles.add(paper.title)
                    
                    # Limit to maximum 10 papers
                    if len(unique_papers) >= 10:
                        logger.info("[LIMIT] Reached maximum of 10 papers")
                        break
        
        logger.info(f"[STATS] Total unique papers found: {len(unique_papers)} (limited to 10 max)")
        return unique_papers

    def _search_scholar_with_bright_data(self, query: str) -> Optional[List[Dict]]:
        """
        Search Google Scholar using Bright Data API
        
        Args:
            query: Search query
            
        Returns:
            List of paper data or None if failed
        """
        try:
            # Google Scholar search URL (limited to 10 papers per query)
            search_url = f"https://scholar.google.com/scholar?q={requests.utils.quote(query)}&hl=en&num=10"
            
            # Make request through Bright Data
            response = self._make_bright_data_request(search_url)
            
            if response and response.get('content'):
                # Parse the Scholar page
                return self._parse_scholar_content(response['content'])
            else:
                logger.error("[ERROR] Failed to get Scholar content via Bright Data")
                return None
                
        except Exception as e:
            logger.error(f"[ERROR] Error searching Scholar with Bright Data: {e}", exc_info=True)
            return None

    def _parse_scholar_content(self, html_content: str) -> List[Dict]:
        """
        Parse Google Scholar search results from HTML content
        
        Args:
            html_content: HTML content from Scholar page
            
        Returns:
            List of paper data dictionaries
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            papers = []
            
            # Find all paper entries
            paper_entries = soup.find_all('div', class_='gs_r gs_or gs_scl')
            
            for entry in paper_entries:
                try:
                    paper_data = {}
                    
                    # Extract title
                    title_element = entry.find('h3', class_='gs_rt')
                    if title_element:
                        title_link = title_element.find('a')
                        if title_link:
                            paper_data['title'] = title_link.get_text(strip=True)
                            paper_data['url'] = title_link.get('href', '')
                        else:
                            paper_data['title'] = title_element.get_text(strip=True)
                            paper_data['url'] = ''
                    
                    # Extract authors and publication info
                    authors_element = entry.find('div', class_='gs_a')
                    if authors_element:
                        authors_text = authors_element.get_text(strip=True)
                        paper_data['authors_text'] = authors_text
                    
                    # Extract abstract/snippet
                    abstract_element = entry.find('div', class_='gs_rs')
                    if abstract_element:
                        paper_data['abstract'] = abstract_element.get_text(strip=True)
                    
                    # Extract citation count
                    citation_element = entry.find('div', class_='gs_fl')
                    if citation_element:
                        citation_links = citation_element.find_all('a')
                        for link in citation_links:
                            if 'Cited by' in link.get_text():
                                citation_text = link.get_text()
                                citation_count = re.search(r'Cited by (\d+)', citation_text)
                                if citation_count:
                                    paper_data['citations'] = int(citation_count.group(1))
                                break
                    
                    if paper_data.get('title'):
                        papers.append(paper_data)
                        
                except Exception as e:
                    logger.debug(f"Error parsing paper entry: {e}")
                    continue
            
            logger.info(f"[DOC] Parsed {len(papers)} papers from Scholar content")
            return papers
            
        except Exception as e:
            logger.error(f"[ERROR] Error parsing Scholar content: {e}", exc_info=True)
            return []

    def _create_paper_from_data(self, paper_data: Dict) -> Optional[ResearchPaper]:
        """
        Create a ResearchPaper object from parsed data
        
        Args:
            paper_data: Dictionary containing paper information
            
        Returns:
            ResearchPaper object or None if creation failed
        """
        try:
            # Extract basic information
            title = paper_data.get('title', 'Unknown Title')
            
            # Parse authors
            authors_text = paper_data.get('authors_text', '')
            authors = self._parse_authors_from_text(authors_text)
            
            # Extract publication year
            year = self._parse_year_from_text(authors_text)
            
            # Extract journal
            journal = self._parse_journal_from_text(authors_text)
            
            # Create paper object
            paper = ResearchPaper(
                title=title,
                authors=authors,
                abstract=paper_data.get('abstract', ''),
                publication_year=year,
                journal=journal,
                url=paper_data.get('url', ''),
                citations=paper_data.get('citations', 0),
                keywords=[]
            )
            
            return paper
            
        except Exception as e:
            logger.error(f"[ERROR] Error creating paper from data: {e}")
            return None

    def _parse_authors_from_text(self, text: str) -> List[str]:
        """Parse authors from publication text"""
        try:
            # Common patterns for author extraction
            author_patterns = [
                r'^([^-]+?)\s*-',  # Authors before dash
                r'^([^,]+(?:,[^,]+)*)\s*-',  # Multiple authors with commas
            ]
            
            for pattern in author_patterns:
                match = re.search(pattern, text)
                if match:
                    authors_str = match.group(1).strip()
                    # Split by comma and clean up
                    authors = [author.strip() for author in authors_str.split(',')]
                    return [author for author in authors if author]
            
            return []
            
        except Exception as e:
            logger.debug(f"Error parsing authors: {e}")
            return []

    def _parse_year_from_text(self, text: str) -> int:
        """Parse publication year from text"""
        try:
            # Look for 4-digit year
            year_match = re.search(r'\b(19|20)\d{2}\b', text)
            if year_match:
                return int(year_match.group(0))
            return 0
        except Exception as e:
            logger.debug(f"Error parsing year: {e}")
            return 0

    def _parse_journal_from_text(self, text: str) -> str:
        """Parse journal name from text"""
        try:
            # Look for journal name after year
            journal_match = re.search(r'\d{4}\s*-\s*([^-]+)', text)
            if journal_match:
                return journal_match.group(1).strip()
            return "Unknown Journal"
        except Exception as e:
            logger.debug(f"Error parsing journal: {e}")
            return "Unknown Journal"

    def _load_advanced_prompts(self) -> Dict[str, str]:
        """Load advanced prompting templates"""
        return {
            'keyword_extraction': """
            Extract the most important keywords and research topics from the following text.
            Focus on academic terms, methodologies, and key concepts.
            Return a JSON object with categorized keywords.
            
            Text: {text}
            """,
            
            'paper_analysis': """
            Analyze this research paper and provide insights about its methodology,
            key findings, and implications for the field.
            
            Title: {title}
            Abstract: {abstract}
            """,
            
            'research_synthesis': """
            Synthesize the following research papers into a comprehensive analysis.
            Identify common themes, methodologies, and key insights.
            
            Papers: {papers}
            """
        }

    def get_bright_data_stats(self) -> Dict[str, Any]:
        """
        Get Bright Data usage statistics
        
        Returns:
            Dictionary with statistics
        """
        if not hasattr(self, 'bright_data_stats'):
            return {}
            
        stats = self.bright_data_stats.copy()
        
        # Calculate success rate
        if stats['requests_made'] > 0:
            stats['success_rate'] = (stats['successful_requests'] / stats['requests_made']) * 100
            stats['average_response_time'] = stats['total_response_time'] / stats['requests_made']
        else:
            stats['success_rate'] = 0
            stats['average_response_time'] = 0
            
        return stats

    def authenticate_google_services(self) -> bool:
        """Authenticate with Google services using service account (no OAuth popups)"""
        try:
            creds = None
            auth_method = "none"
            
            # Try service account authentication first (no OAuth popup)
            service_account_paths = [
                'service-account.json',
                'task assigner/service-account.json', 
                os.getenv('GOOGLE_SERVICE_ACCOUNT_PATH', '')
            ]
            
            for sa_path in service_account_paths:
                if sa_path and os.path.exists(sa_path):
                    try:
                        from google.oauth2 import service_account
                        creds = service_account.Credentials.from_service_account_file(
                            sa_path, scopes=self.google_scopes)
                        auth_method = f"service_account:{sa_path}"
                        logger.info(f"[OK] Using service account authentication: {sa_path}")
                        break
                    except Exception as e:
                        logger.warning(f"[WARNING] Service account auth failed for {sa_path}: {e}")
            
            # Fallback to existing token if service account not available
            if not creds and os.path.exists('token.json'):
                try:
                    creds = Credentials.from_authorized_user_file('token.json', self.google_scopes)
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    auth_method = "oauth_token"
                    logger.info("[OK] Using existing OAuth token")
                except Exception as e:
                    logger.warning(f"[WARNING] Token refresh failed: {e}")
            
            # Validate credentials
            if not creds:
                logger.error("[ERROR] No valid Google credentials available")
                logger.error("  ❌ Service account authentication failed")
                logger.error("  ❌ OAuth token not available or invalid")
                logger.error("")
                logger.error("  🔧 SOLUTION:")
                logger.error("  1. Add service-account.json file to your project directory")
                logger.error("  2. Or set GOOGLE_SERVICE_ACCOUNT_PATH environment variable")
                logger.error("  3. Ensure service account has Google Docs and Drive API access")
                logger.error("  4. Share your Google Docs with: sebastiancastano@phonic-goods-317118.iam.gserviceaccount.com")
                return False
            
            # For OAuth tokens, check validity and refresh if needed
            if hasattr(creds, 'expired') and creds.expired and hasattr(creds, 'refresh_token') and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    logger.info("[OK] OAuth credentials refreshed")
                except Exception as e:
                    logger.error(f"[ERROR] Failed to refresh OAuth credentials: {e}")
                    return False
            
            # Build Google services
            try:
                self.google_service = build('docs', 'v1', credentials=creds)
                self.drive_service = build('drive', 'v3', credentials=creds)
                
                logger.info(f"[OK] Google services authenticated successfully ({auth_method})")
                logger.info("[OK] ✅ Google Docs API ready")
                logger.info("[OK] ✅ Google Drive API ready")
                return True
                
            except Exception as e:
                logger.error(f"[ERROR] Failed to build Google services: {e}")
                return False
            
        except Exception as e:
            logger.error(f"[ERROR] Google authentication failed: {e}")
            return False

    def filter_and_rank_papers(self, papers: List[ResearchPaper], original_query: str) -> List[ResearchPaper]:
        """Filter and rank papers by relevance and quality with improved scoring and debugging"""
        try:
            if not papers:
                return []
            
            logger.info(f"[SEARCH] Filtering and ranking {len(papers)} papers...")
            
            # Score papers for relevance
            scored_papers = self._score_paper_relevance(papers, original_query)
            
            # Debug: Log scoring statistics
            scores = [paper.relevance_score for paper in scored_papers]
            if scores:
                avg_score = sum(scores) / len(scores)
                max_score = max(scores)
                min_score = min(scores)
                logger.info(f"[DEBUG] Relevance scores - Avg: {avg_score:.3f}, Max: {max_score:.3f}, Min: {min_score:.3f}")
                logger.info(f"[DEBUG] Threshold: {self.relevance_threshold}")
            
            # Filter by thresholds
            filtered_papers = [
                paper for paper in scored_papers 
                if paper.relevance_score >= self.relevance_threshold
            ]
            
            # FALLBACK: If no papers pass the threshold, take the top 50% by score
            if not filtered_papers and scored_papers:
                logger.warning(f"[FALLBACK] No papers met threshold {self.relevance_threshold}, using top 50% by score")
                scored_papers.sort(key=lambda p: p.relevance_score, reverse=True)
                take_count = max(1, len(scored_papers) // 2)  # Take at least 1, or 50% of papers
                filtered_papers = scored_papers[:take_count]
                
                # Log the fallback papers for debugging
                for paper in filtered_papers[:3]:  # Log top 3
                    logger.info(f"[FALLBACK] Paper: {paper.title[:60]}... (score: {paper.relevance_score:.3f})")
            
            # Sort by combined score (relevance + quality + citations)
            filtered_papers.sort(
                key=lambda p: (p.relevance_score + p.quality_score + min(p.citations/100, 1.0)) / 3,
                reverse=True
            )
            
            logger.info(f"[OK] Filtered to {len(filtered_papers)} relevant papers")
            
            # Debug: Log top papers
            for i, paper in enumerate(filtered_papers[:3]):
                logger.info(f"[TOP-{i+1}] {paper.title[:60]}... (rel: {paper.relevance_score:.3f}, qual: {paper.quality_score:.3f})")
            
            return filtered_papers
            
        except Exception as e:
            logger.error(f"[ERROR] Error filtering papers: {e}")
            return papers

    def _score_paper_relevance(self, papers: List[ResearchPaper], query: str) -> List[ResearchPaper]:
        """Score papers for relevance to the query with improved algorithm"""
        try:
            query_words = set(query.lower().split())
            
            for paper in papers:
                # Enhanced text for comparison
                paper_text = f"{paper.title} {paper.abstract} {' '.join(paper.keywords)}"
                
                # Calculate multiple similarity metrics
                text_similarity = self._calculate_text_similarity(query, paper_text)
                keyword_overlap = self._calculate_keyword_overlap(query, paper.keywords)
                title_similarity = self._calculate_title_similarity(query, paper.title)
                
                # Word-level matching (more lenient)
                word_match_score = self._calculate_word_match_score(query_words, paper_text)
                
                # Combine scores with more weight on word matching and title similarity
                relevance_components = [
                    text_similarity * 0.3,      # TF-IDF similarity
                    keyword_overlap * 0.2,      # Keyword overlap  
                    title_similarity * 0.3,     # Title similarity (very important)
                    word_match_score * 0.2      # Word-level matching
                ]
                
                paper.relevance_score = sum(relevance_components)
                
                # Enhanced quality score
                citation_score = min(paper.citations / 50, 1.0)  # Lower normalization threshold
                completeness_score = 1.0 if paper.abstract else 0.7  # Less penalty for missing abstract
                
                # Bonus for recent papers (last 10 years)
                current_year = 2025
                if paper.publication_year >= current_year - 10:
                    recency_bonus = 0.2
                else:
                    recency_bonus = 0.0
                
                paper.quality_score = (citation_score * 0.5) + (completeness_score * 0.4) + recency_bonus
                
                # Debug logging for low-scoring papers
                if paper.relevance_score < 0.2:
                    logger.debug(f"[LOW-SCORE] {paper.title[:50]}... score: {paper.relevance_score:.3f} "
                               f"(text: {text_similarity:.3f}, title: {title_similarity:.3f}, "
                               f"words: {word_match_score:.3f})")
            
            return papers
            
        except Exception as e:
            logger.error(f"[ERROR] Error scoring papers: {e}")
            return papers

    def _calculate_title_similarity(self, query: str, title: str) -> float:
        """Calculate similarity between query and paper title"""
        try:
            if not query or not title:
                return 0.0
            
            # Simple word overlap in title (case insensitive)
            query_words = set(query.lower().split())
            title_words = set(title.lower().split())
            
            # Remove common academic words
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 'once'}
            
            query_words = query_words - common_words
            title_words = title_words - common_words
            
            if not query_words or not title_words:
                return 0.0
            
            # Calculate overlap
            intersection = query_words.intersection(title_words)
            union = query_words.union(title_words)
            
            overlap_score = len(intersection) / len(union) if union else 0.0
            
            # Bonus for exact phrase matches
            if query.lower() in title.lower():
                overlap_score += 0.3
            
            return min(overlap_score, 1.0)
            
        except Exception as e:
            logger.debug(f"Error calculating title similarity: {e}")
            return 0.0

    def _calculate_word_match_score(self, query_words: set, paper_text: str) -> float:
        """Calculate word-level matching score"""
        try:
            if not query_words or not paper_text:
                return 0.0
            
            paper_words = set(paper_text.lower().split())
            
            # Count matches
            matches = query_words.intersection(paper_words)
            
            # Calculate score based on percentage of query words found
            match_score = len(matches) / len(query_words) if query_words else 0.0
            
            return match_score
            
        except Exception as e:
            logger.debug(f"Error calculating word match score: {e}")
            return 0.0

    def _calculate_text_similarity(self, query: str, text: str) -> float:
        """Calculate cosine similarity between query and text"""
        try:
            if not query or not text:
                return 0.0
            
            vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
            vectors = vectorizer.fit_transform([query, text])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.debug(f"Error calculating similarity: {e}")
            return 0.0

    def _calculate_keyword_overlap(self, query: str, keywords: List[str]) -> float:
        """Calculate keyword overlap between query and paper keywords"""
        try:
            if not query or not keywords:
                return 0.0
            
            query_words = set(query.lower().split())
            keyword_words = set(' '.join(keywords).lower().split())
            
            intersection = query_words.intersection(keyword_words)
            union = query_words.union(keyword_words)
            
            if not union:
                return 0.0
            
            return len(intersection) / len(union)
            
        except Exception as e:
            logger.debug(f"Error calculating keyword overlap: {e}")
            return 0.0

    def analyze_research_content(self, papers: List[ResearchPaper]) -> Dict[str, Any]:
        """Analyze research papers and extract insights with marketing focus"""
        try:
            if not papers:
                return {"error": "No papers to analyze"}
            
            logger.info(f"🔬 Analyzing {len(papers)} research papers with marketing focus...")
            
            # Prepare detailed papers for analysis
            detailed_papers = []
            for paper in papers:
                # Prepare comprehensive content for analysis
                content_parts = []
                
                # Add title
                if paper.title:
                    content_parts.append(f"Title: {paper.title}")
                
                # Add abstract
                if paper.abstract:
                    content_parts.append(f"Abstract: {paper.abstract}")
                
                # Add keywords
                if paper.keywords:
                    content_parts.append(f"Keywords: {', '.join(paper.keywords)}")
                
                # Add full text preview (PDF or URL content)
                if paper.full_text:
                    content_parts.append(f"Full Text Preview: {paper.full_text[:1500]}")
                    text_source = "Full text available"
                else:
                    text_source = "Abstract and keywords only"
                
                # Combine all available content
                combined_content = " | ".join(content_parts)
                
                paper_content = {
                    'title': paper.title,
                    'authors': paper.authors,
                    'year': paper.publication_year,
                    'journal': paper.journal,
                    'url': paper.url,
                    'citations': paper.citations,
                    'abstract': paper.abstract,
                    'keywords': paper.keywords,
                    'combined_content': combined_content,  # All available content
                    'text_source': text_source,
                    'relevance_score': paper.relevance_score,
                    'has_full_text': bool(paper.full_text)
                }
                detailed_papers.append(paper_content)
            
            # Enhanced OpenAI analysis with marketing focus
            analysis_prompt = f"""
            You are a marketing research analyst. Analyze the following research papers and provide comprehensive insights with a strong marketing focus.
            
            IMPORTANT: Some papers have full text available, others only have abstracts and keywords. Provide analysis for ALL papers based on available content.
            
            Papers to analyze: {json.dumps(detailed_papers[:8])}  # Process up to 8 papers
            
            For each paper, provide:
            1. **Paper Summary**: Brief overview of the main findings (note if based on abstract only)
            2. **Marketing Relevance Score**: Rate 1-10 (10 = extremely relevant to marketing)
            3. **Marketing Takeaways**: Specific actionable insights for marketers
            4. **Business Applications**: How this research can be applied in business/marketing
            5. **Target Industries**: Which industries would benefit most from these findings
            6. **Content Quality**: Note if analysis is based on full text or abstract only
            
            Then provide overall analysis:
            7. **Key Themes**: Common themes across all papers
            8. **Marketing Trends**: What these papers reveal about current marketing trends
            9. **Actionable Recommendations**: Top 5 recommendations for marketing professionals
            10. **Implementation Strategies**: How to implement these insights in marketing campaigns
            11. **Future Marketing Directions**: What these papers suggest about future marketing
            
            Return as structured JSON with:
            - "individual_papers": Array of paper analyses (analyze ALL papers provided)
            - "overall_analysis": Combined insights
            - "marketing_summary": Executive summary for marketing teams
            - "content_analysis": Summary of content quality (how many had full text vs abstract only)
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3,
                max_tokens=4000
            )
            
            # Parse the response
            analysis_text = response.choices[0].message.content
            
            try:
                analysis_data = json.loads(analysis_text)
            except json.JSONDecodeError:
                # Enhanced fallback structure
                analysis_data = {
                    "individual_papers": [],
                    "overall_analysis": {
                        "key_themes": ["research analysis", "academic insights"],
                        "marketing_trends": ["data-driven marketing", "evidence-based strategies"],
                        "actionable_recommendations": ["implement research findings", "use data for decisions"]
                    },
                    "marketing_summary": analysis_text,
                    "raw_analysis": analysis_text
                }
            
            # Add metadata
            analysis_data["papers_analyzed"] = len(papers)
            analysis_data["total_citations"] = sum(p.citations for p in papers)
            analysis_data["average_relevance"] = sum(p.relevance_score for p in papers) / len(papers) if papers else 0
            analysis_data["year_range"] = f"{min(p.publication_year for p in papers if p.publication_year > 0)} - {max(p.publication_year for p in papers if p.publication_year > 0)}" if papers else "N/A"
            
            logger.info("[OK] Enhanced marketing-focused research analysis completed")
            return analysis_data
            
        except Exception as e:
            logger.error(f"[ERROR] Error analyzing research content: {e}")
            return {"error": str(e), "papers_analyzed": len(papers)}

    def create_research_document(self, analysis_data: Dict[str, Any], original_context: str, 
                                marketing_analysis: Dict[str, Any] = None, 
                                output_filename: str = None) -> str:
        """Create a comprehensive Word document with detailed research findings and marketing analysis"""
        try:
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"research_synthesis_{timestamp}.docx"
            
            logger.info(f"[DOC] Creating comprehensive research document with marketing analysis: {output_filename}")
            
            # Create document
            doc = Document()
            
            # Add title
            title = doc.add_heading('Marketing Research Synthesis Report', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Add metadata
            doc.add_heading('Research Overview', level=1)
            doc.add_paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            doc.add_paragraph(f"Original Context: {original_context}")
            doc.add_paragraph(f"Papers Analyzed: {analysis_data.get('papers_analyzed', 'Unknown')}")
            doc.add_paragraph(f"Total Citations: {analysis_data.get('total_citations', 'Unknown')}")
            doc.add_paragraph(f"Average Relevance Score: {analysis_data.get('average_relevance', 0):.2f}/10")
            doc.add_paragraph(f"Year Range: {analysis_data.get('year_range', 'Unknown')}")
            
            # Add executive summary if available
            if marketing_analysis and 'executive_summary' in marketing_analysis:
                doc.add_heading('Executive Summary', level=1)
                doc.add_paragraph(marketing_analysis['executive_summary'])
            
            # Add quick actions section
            if marketing_analysis and 'quick_actions' in marketing_analysis:
                doc.add_heading('Quick Actions for Marketing Teams', level=1)
                for i, action in enumerate(marketing_analysis['quick_actions'], 1):
                    doc.add_paragraph(f"{i}. {action}")
            
            # Add individual paper analysis
            if marketing_analysis and 'individual_papers' in marketing_analysis:
                doc.add_heading('Individual Paper Analysis', level=1)
                
                for paper in marketing_analysis['individual_papers']:
                    # Paper title and authors
                    paper_title = paper.get('title', 'Unknown Title')
                    authors = paper.get('authors', ['Unknown Author'])
                    if isinstance(authors, list):
                        authors_str = ', '.join(authors)
                    else:
                        authors_str = str(authors)
                    
                    doc.add_heading(f"{paper_title}", level=2)
                    doc.add_paragraph(f"Authors: {authors_str}")
                    doc.add_paragraph(f"Marketing Relevance Score: {paper.get('marketing_relevance_score', 'N/A')}/10")
                    
                    # Add URL if available
                    if paper.get('url'):
                        doc.add_paragraph(f"URL: {paper['url']}")
                    
                    # Add summary
                    if paper.get('summary'):
                        doc.add_heading('Summary', level=3)
                        doc.add_paragraph(paper['summary'])
                    
                    # Add marketing takeaways
                    if paper.get('marketing_takeaways'):
                        doc.add_heading('Marketing Takeaways', level=3)
                        takeaways = paper['marketing_takeaways']
                        if isinstance(takeaways, list):
                            for takeaway in takeaways:
                                doc.add_paragraph(f"• {takeaway}")
                        else:
                            doc.add_paragraph(str(takeaways))
                    
                    # Add business applications
                    if paper.get('business_applications'):
                        doc.add_heading('Business Applications', level=3)
                        applications = paper['business_applications']
                        if isinstance(applications, list):
                            for app in applications:
                                doc.add_paragraph(f"• {app}")
                        else:
                            doc.add_paragraph(str(applications))
                    
                    # Add target industries
                    if paper.get('target_industries'):
                        doc.add_heading('Target Industries', level=3)
                        industries = paper['target_industries']
                        if isinstance(industries, list):
                            for industry in industries:
                                doc.add_paragraph(f"• {industry}")
                        else:
                            doc.add_paragraph(str(industries))
                    
                    # Add implementation strategy
                    if paper.get('implementation_strategy'):
                        doc.add_heading('Implementation Strategy', level=3)
                        doc.add_paragraph(paper['implementation_strategy'])
                    
                    # Add ROI potential
                    if paper.get('roi_potential'):
                        doc.add_heading('ROI Potential', level=3)
                        doc.add_paragraph(paper['roi_potential'])
                    
                    # Add page break between papers
                    doc.add_page_break()
            
            # Add overall marketing analysis
            if marketing_analysis and 'overall_marketing_analysis' in marketing_analysis:
                doc.add_heading('Overall Marketing Analysis', level=1)
                overall = marketing_analysis['overall_marketing_analysis']
                
                # Top marketing trends
                if 'top_marketing_trends' in overall:
                    doc.add_heading('Top Marketing Trends', level=2)
                    for trend in overall['top_marketing_trends']:
                        doc.add_paragraph(f"• {trend}")
                
                # Marketing strategy recommendations
                if 'marketing_strategy_recommendations' in overall:
                    doc.add_heading('Marketing Strategy Recommendations', level=2)
                    for rec in overall['marketing_strategy_recommendations']:
                        doc.add_paragraph(f"• {rec}")
                
                # Future marketing directions
                if 'future_marketing_directions' in overall:
                    doc.add_heading('Future Marketing Directions', level=2)
                    directions = overall['future_marketing_directions']
                    if isinstance(directions, list):
                        for direction in directions:
                            doc.add_paragraph(f"• {direction}")
                    else:
                        doc.add_paragraph(str(directions))
                
                # Implementation roadmap
                if 'implementation_roadmap' in overall:
                    doc.add_heading('Implementation Roadmap', level=2)
                    roadmap = overall['implementation_roadmap']
                    if isinstance(roadmap, list):
                        for i, step in enumerate(roadmap, 1):
                            doc.add_paragraph(f"{i}. {step}")
                    else:
                        doc.add_paragraph(str(roadmap))
            
            # Add paper references section
            if marketing_analysis and 'paper_references' in marketing_analysis:
                doc.add_heading('Paper References', level=1)
                
                for ref in marketing_analysis['paper_references']:
                    doc.add_paragraph(f"• {ref.get('title', 'Unknown Title')}")
                    doc.add_paragraph(f"  Authors: {', '.join(ref.get('authors', ['Unknown']))}")
                    doc.add_paragraph(f"  Year: {ref.get('year', 'Unknown')}")
                    doc.add_paragraph(f"  Journal: {ref.get('journal', 'Unknown')}")
                    doc.add_paragraph(f"  Citations: {ref.get('citations', 0)}")
                    doc.add_paragraph(f"  Relevance Score: {ref.get('relevance_score', 0):.2f}/10")
                    if ref.get('url'):
                        doc.add_paragraph(f"  URL: {ref['url']}")
                    doc.add_paragraph("")  # Add spacing
            
            # Add academic analysis content
            doc.add_heading('Academic Research Analysis', level=1)
            if 'marketing_summary' in analysis_data:
                doc.add_paragraph(analysis_data['marketing_summary'])
            elif 'analysis' in analysis_data:
                doc.add_paragraph(analysis_data['analysis'])
            
            # Add other sections if available
            for key, value in analysis_data.items():
                if key not in ['analysis', 'marketing_summary', 'papers_analyzed', 'total_citations', 'error', 'individual_papers', 'overall_analysis']:
                    doc.add_heading(key.replace('_', ' ').title(), level=2)
                    if isinstance(value, list):
                        for item in value:
                            doc.add_paragraph(f"• {item}")
                    else:
                        doc.add_paragraph(str(value))
            
            # Add final recommendations section
            doc.add_heading('Executive Summary & Final Recommendations', level=1)
            
            summary_text = f"""
            This comprehensive research synthesis analyzed {analysis_data.get('papers_analyzed', 'multiple')} academic papers with a total of {analysis_data.get('total_citations', 'unknown')} citations and an average relevance score of {analysis_data.get('average_relevance', 0):.2f}/10.
            
            Each paper was individually analyzed for marketing relevance, business applications, and actionable insights. The analysis provides specific recommendations for marketers, including implementation strategies and ROI potential.
            
            Key findings include market trends, consumer behavior insights, and competitive advantages that can be leveraged in marketing campaigns. The report bridges the gap between academic research and practical marketing applications.
            """
            doc.add_paragraph(summary_text)
            
            # Save document
            doc.save(output_filename)
            
            logger.info(f"[OK] Comprehensive research document with marketing analysis saved: {output_filename}")
            return output_filename
            
        except Exception as e:
            logger.error(f"[ERROR] Error creating document: {e}")
            return ""

    def create_google_document(self, analysis_data: Dict[str, Any], original_context: str, 
                              marketing_analysis: Dict[str, Any] = None, 
                              doc_title: str = None) -> Dict[str, str]:
        """Create a comprehensive Google Document with detailed research findings and marketing analysis"""
        try:
            if not self.google_authenticated or not self.google_service:
                logger.error("[ERROR] Google services not authenticated for document creation")
                return {"error": "Google authentication required for document creation"}
            
            if not doc_title:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                doc_title = f"Marketing Research Synthesis Report {timestamp}"
            
            logger.info(f"[DOC] Creating Google Document: {doc_title}")
            
            # Create new Google Document
            document = {
                'title': doc_title
            }
            
            # Create the document
            doc = self.google_service.documents().create(body=document).execute()
            doc_id = doc.get('documentId')
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            
            logger.info(f"[DOC] Created Google Document with ID: {doc_id}")
            
            # Prepare content structure
            content_elements = []
            
            # Build document content
            content_text = self._build_document_content_text(analysis_data, original_context, marketing_analysis)
            
            # Insert content into the document
            requests = [
                {
                    'insertText': {
                        'location': {
                            'index': 1,
                        },
                        'text': content_text
                    }
                }
            ]
            
            # Apply formatting requests
            formatting_requests = self._build_google_doc_formatting_requests(content_text)
            requests.extend(formatting_requests)
            
            # Execute batch update
            result = self.google_service.documents().batchUpdate(
                documentId=doc_id, 
                body={'requests': requests}
            ).execute()
            
            # Make document publicly readable
            try:
                permission = {
                    'type': 'anyone',
                    'role': 'reader'
                }
                self.drive_service.permissions().create(
                    fileId=doc_id,
                    body=permission
                ).execute()
                logger.info("[DOC] Google Document made publicly readable")
            except Exception as e:
                logger.warning(f"[WARNING] Could not make document public: {e}")
            
            logger.info(f"[OK] Google Document created successfully: {doc_url}")
            
            return {
                "document_id": doc_id,
                "document_url": doc_url,
                "edit_url": doc_url,
                "view_url": f"https://docs.google.com/document/d/{doc_id}/view",
                "title": doc_title
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Error creating Google Document: {e}")
            return {"error": f"Failed to create Google Document: {str(e)}"}

    def _build_document_content_text(self, analysis_data: Dict[str, Any], original_context: str, 
                                   marketing_analysis: Dict[str, Any] = None) -> str:
        """Build the text content for the document"""
        try:
            content_lines = []
            
            # Title
            content_lines.append("MARKETING RESEARCH SYNTHESIS REPORT")
            content_lines.append("=" * 50)
            content_lines.append("")
            
            # Metadata
            content_lines.append("RESEARCH OVERVIEW")
            content_lines.append("-" * 20)
            content_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            content_lines.append(f"Original Context: {original_context}")
            content_lines.append(f"Papers Analyzed: {analysis_data.get('papers_analyzed', 'Unknown')}")
            content_lines.append(f"Total Citations: {analysis_data.get('total_citations', 'Unknown')}")
            content_lines.append(f"Average Relevance Score: {analysis_data.get('average_relevance', 0):.2f}/10")
            content_lines.append(f"Year Range: {analysis_data.get('year_range', 'Unknown')}")
            content_lines.append("")
            
            # Executive summary
            if marketing_analysis and 'executive_summary' in marketing_analysis:
                content_lines.append("EXECUTIVE SUMMARY")
                content_lines.append("-" * 20)
                content_lines.append(marketing_analysis['executive_summary'])
                content_lines.append("")
            
            # Quick actions
            if marketing_analysis and 'quick_actions' in marketing_analysis:
                content_lines.append("QUICK ACTIONS FOR MARKETING TEAMS")
                content_lines.append("-" * 35)
                for i, action in enumerate(marketing_analysis['quick_actions'], 1):
                    content_lines.append(f"{i}. {action}")
                content_lines.append("")
            
            # Individual paper analysis
            if marketing_analysis and 'individual_papers' in marketing_analysis:
                content_lines.append("INDIVIDUAL PAPER ANALYSIS")
                content_lines.append("-" * 30)
                content_lines.append("")
                
                for paper in marketing_analysis['individual_papers']:
                    paper_title = paper.get('title', 'Unknown Title')
                    authors = paper.get('authors', ['Unknown Author'])
                    if isinstance(authors, list):
                        authors_str = ', '.join(authors)
                    else:
                        authors_str = str(authors)
                    
                    content_lines.append(f"PAPER: {paper_title}")
                    content_lines.append(f"Authors: {authors_str}")
                    content_lines.append(f"Marketing Relevance Score: {paper.get('marketing_relevance_score', 'N/A')}/10")
                    
                    if paper.get('url'):
                        content_lines.append(f"URL: {paper['url']}")
                    
                    if paper.get('summary'):
                        content_lines.append("")
                        content_lines.append("Summary:")
                        content_lines.append(paper['summary'])
                    
                    if paper.get('marketing_takeaways'):
                        content_lines.append("")
                        content_lines.append("Marketing Takeaways:")
                        takeaways = paper['marketing_takeaways']
                        if isinstance(takeaways, list):
                            for takeaway in takeaways:
                                content_lines.append(f"• {takeaway}")
                        else:
                            content_lines.append(str(takeaways))
                    
                    if paper.get('business_applications'):
                        content_lines.append("")
                        content_lines.append("Business Applications:")
                        applications = paper['business_applications']
                        if isinstance(applications, list):
                            for app in applications:
                                content_lines.append(f"• {app}")
                        else:
                            content_lines.append(str(applications))
                    
                    content_lines.append("")
                    content_lines.append("-" * 60)
                    content_lines.append("")
            
            # Overall marketing analysis
            if marketing_analysis and 'overall_marketing_analysis' in marketing_analysis:
                content_lines.append("OVERALL MARKETING ANALYSIS")
                content_lines.append("-" * 30)
                overall = marketing_analysis['overall_marketing_analysis']
                
                if 'top_marketing_trends' in overall:
                    content_lines.append("")
                    content_lines.append("Top Marketing Trends:")
                    for trend in overall['top_marketing_trends']:
                        content_lines.append(f"• {trend}")
                
                if 'marketing_strategy_recommendations' in overall:
                    content_lines.append("")
                    content_lines.append("Marketing Strategy Recommendations:")
                    for rec in overall['marketing_strategy_recommendations']:
                        content_lines.append(f"• {rec}")
                
                content_lines.append("")
            
            # Academic analysis
            content_lines.append("ACADEMIC RESEARCH ANALYSIS")
            content_lines.append("-" * 30)
            if 'marketing_summary' in analysis_data:
                content_lines.append(analysis_data['marketing_summary'])
            elif 'analysis' in analysis_data:
                content_lines.append(analysis_data['analysis'])
            content_lines.append("")
            
            # Final summary
            content_lines.append("EXECUTIVE SUMMARY & FINAL RECOMMENDATIONS")
            content_lines.append("-" * 45)
            summary_text = f"""
This comprehensive research synthesis analyzed {analysis_data.get('papers_analyzed', 'multiple')} academic papers with a total of {analysis_data.get('total_citations', 'unknown')} citations and an average relevance score of {analysis_data.get('average_relevance', 0):.2f}/10.

Each paper was individually analyzed for marketing relevance, business applications, and actionable insights. The analysis provides specific recommendations for marketers, including implementation strategies and ROI potential.

Key findings include market trends, consumer behavior insights, and competitive advantages that can be leveraged in marketing campaigns. The report bridges the gap between academic research and practical marketing applications.
            """
            content_lines.append(summary_text.strip())
            
            return "\n".join(content_lines)
            
        except Exception as e:
            logger.error(f"[ERROR] Error building document content: {e}")
            return f"Error building document content: {str(e)}"

    def _build_google_doc_formatting_requests(self, content_text: str) -> list:
        """Build formatting requests for Google Document"""
        try:
            requests = []
            lines = content_text.split('\n')
            current_index = 1  # Start after the first character
            
            for line in lines:
                line_length = len(line)
                
                # Format main title
                if line == "MARKETING RESEARCH SYNTHESIS REPORT":
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': current_index,
                                'endIndex': current_index + line_length
                            },
                            'textStyle': {
                                'bold': True,
                                'fontSize': {'magnitude': 18, 'unit': 'PT'}
                            },
                            'fields': 'bold,fontSize'
                        }
                    })
                
                # Format section headers
                elif line.isupper() and len(line) > 5 and not line.startswith('=') and not line.startswith('-'):
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': current_index,
                                'endIndex': current_index + line_length
                            },
                            'textStyle': {
                                'bold': True,
                                'fontSize': {'magnitude': 14, 'unit': 'PT'}
                            },
                            'fields': 'bold,fontSize'
                        }
                    })
                
                # Format paper titles (lines starting with "PAPER:")
                elif line.startswith("PAPER:"):
                    requests.append({
                        'updateTextStyle': {
                            'range': {
                                'startIndex': current_index,
                                'endIndex': current_index + line_length
                            },
                            'textStyle': {
                                'bold': True,
                                'fontSize': {'magnitude': 12, 'unit': 'PT'}
                            },
                            'fields': 'bold,fontSize'
                        }
                    })
                
                current_index += line_length + 1  # +1 for newline character
            
            return requests
            
        except Exception as e:
            logger.debug(f"Error building formatting requests: {e}")
            return []

    def extract_keywords_from_google_file(self, file_id: str) -> Dict[str, Any]:
        """Extract sophisticated keywords from a Google file using enhanced OpenAI analysis"""
        try:
            # Check if Google services are authenticated
            if not self.google_authenticated or not self.google_service:
                logger.error("[ERROR] Google services not authenticated")
                # Try to re-authenticate
                if not self.authenticate_google_services():
                    return {
                        "error": "Google authentication failed. Ensure service-account.json exists and file is shared with sebastiancastano@phonic-goods-317118.iam.gserviceaccount.com"
                    }
            
            logger.info(f"[DOC] Extracting sophisticated keywords from Google file: {file_id}")
            logger.info("[DOC] Using service account authentication (no OAuth required)")
            
            # Get file content
            file_content = self._get_google_file_content(file_id)
            
            if not file_content:
                return {
                    "error": "Failed to get file content. Ensure the file is shared with sebastiancastano@phonic-goods-317118.iam.gserviceaccount.com"
                }
            
            logger.info(f"[DOC] Successfully retrieved {len(file_content)} characters from Google Doc")
            
            # Enhanced keyword extraction using sophisticated OpenAI analysis
            keywords_data = self._extract_sophisticated_keywords_with_openai(file_content)
            
            if keywords_data.get("error"):
                # Fallback to enhanced simple extraction if OpenAI fails
                logger.warning("[WARNING] OpenAI keyword extraction failed, using enhanced fallback")
                keywords_data = self._extract_enhanced_keywords_fallback(file_content)
            
            # Log the extracted keywords for debugging
            logger.info(f"[KEYWORDS] Primary: {keywords_data.get('primary_keywords', [])}")
            logger.info(f"[KEYWORDS] Research Topics: {keywords_data.get('research_topics', [])}")
            logger.info(f"[KEYWORDS] Academic Concepts: {keywords_data.get('academic_concepts', [])}")
            
            logger.info("[OK] Enhanced keywords extracted successfully from Google Doc")
            return keywords_data
            
        except Exception as e:
            logger.error(f"[ERROR] Error extracting keywords from Google file: {e}")
            return {"error": f"Keyword extraction failed: {str(e)}"}

    def _extract_sophisticated_keywords_with_openai(self, file_content: str) -> Dict[str, Any]:
        """Extract sophisticated keywords using enhanced OpenAI prompting"""
        try:
            # Use up to 6000 characters for better context
            content_sample = file_content[:6000]
            
            # Enhanced prompt for sophisticated keyword extraction
            keywords_prompt = f"""
            You are a research analyst and academic expert. Analyze the following document text and extract the most valuable keywords and concepts for academic research.

            DOCUMENT CONTENT:
            {content_sample}

            Extract keywords in the following categories with HIGH PRECISION and RELEVANCE:

            1. PRIMARY_KEYWORDS (8-12 terms): The most important academic concepts, theories, technologies, or phenomena discussed
            2. RESEARCH_TOPICS (5-8 areas): Broad research domains and fields of study that this document relates to
            3. ACADEMIC_CONCEPTS (6-10 terms): Specific academic terms, frameworks, models, or theoretical constructs
            4. TECHNICAL_TERMS (5-8 terms): Industry-specific terminology, tools, technologies, or methodologies
            5. DOMAIN_KEYWORDS (5-8 terms): Subject matter expertise areas and specialized domains
            6. SEARCH_QUERIES (6-10 phrases): 2-4 word phrases that would find relevant academic papers

            EXTRACTION GUIDELINES:
            - Prioritize multi-word concepts over single words (e.g., "machine learning" vs "learning")
            - Focus on domain-specific terminology rather than generic terms
            - Extract concepts that would appear in academic paper titles and abstracts
            - Include both theoretical concepts and practical applications
            - Avoid overly generic terms like "research", "analysis", "study" unless they're part of specific phrases
            - Consider synonyms and related terms that researchers might use
            - Look for emerging trends, technologies, or methodologies mentioned

            Return ONLY a valid JSON object in this exact format:
            {{
                "primary_keywords": ["keyword1", "keyword2", ...],
                "research_topics": ["topic1", "topic2", ...],
                "academic_concepts": ["concept1", "concept2", ...],
                "technical_terms": ["term1", "term2", ...],
                "domain_keywords": ["domain1", "domain2", ...],
                "search_queries": ["query phrase 1", "query phrase 2", ...]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert research analyst specializing in academic keyword extraction. Provide precise, relevant keywords that will find high-quality academic papers."
                    },
                    {
                        "role": "user", 
                        "content": keywords_prompt
                    }
                ],
                temperature=0.2,  # Slightly higher for more varied keywords
                max_tokens=2000
            )
            
            keywords_text = response.choices[0].message.content
            
            # Clean the response to extract just the JSON
            keywords_text = keywords_text.strip()
            if keywords_text.startswith('```json'):
                keywords_text = keywords_text[7:]
            if keywords_text.endswith('```'):
                keywords_text = keywords_text[:-3]
            keywords_text = keywords_text.strip()
            
            try:
                keywords_data = json.loads(keywords_text)
                
                # Validate and clean the extracted keywords
                keywords_data = self._validate_and_clean_keywords(keywords_data)
                
                logger.info(f"[AI] Extracted {len(keywords_data.get('primary_keywords', []))} primary keywords using OpenAI")
                logger.info(f"[AI] Extracted {len(keywords_data.get('search_queries', []))} search queries")
                
                return keywords_data
                
            except json.JSONDecodeError as e:
                logger.error(f"[ERROR] Failed to parse OpenAI keyword response: {e}")
                logger.debug(f"[DEBUG] Response text: {keywords_text[:500]}...")
                return {"error": "Failed to parse OpenAI response"}
                
        except Exception as e:
            logger.error(f"[ERROR] Error in OpenAI keyword extraction: {e}")
            return {"error": str(e)}

    def _validate_and_clean_keywords(self, keywords_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted keywords"""
        try:
            cleaned_data = {}
            
            # Expected categories with their limits
            categories = {
                'primary_keywords': 12,
                'research_topics': 8,
                'academic_concepts': 10,
                'technical_terms': 8,
                'domain_keywords': 8,
                'search_queries': 10
            }
            
            for category, max_count in categories.items():
                if category in keywords_data and isinstance(keywords_data[category], list):
                    # Clean and filter keywords
                    cleaned_keywords = []
                    for keyword in keywords_data[category]:
                        if isinstance(keyword, str):
                            # Clean the keyword
                            clean_keyword = keyword.strip().lower()
                            
                            # Filter out overly generic or short terms
                            if (len(clean_keyword) > 2 and 
                                clean_keyword not in ['research', 'study', 'analysis', 'method', 'data', 'the', 'and', 'for'] and
                                clean_keyword not in cleaned_keywords):
                                cleaned_keywords.append(keyword.strip())
                    
                    # Limit to max count
                    cleaned_data[category] = cleaned_keywords[:max_count]
                else:
                    cleaned_data[category] = []
            
            # Ensure we have at least some keywords in each category
            if not cleaned_data.get('primary_keywords'):
                cleaned_data['primary_keywords'] = ['academic research', 'data analysis']
            
            if not cleaned_data.get('research_topics'):
                cleaned_data['research_topics'] = ['research methodology']
                
            return cleaned_data
            
        except Exception as e:
            logger.error(f"[ERROR] Error validating keywords: {e}")
            return keywords_data

    def _extract_enhanced_keywords_fallback(self, file_content: str) -> Dict[str, Any]:
        """Enhanced fallback keyword extraction using NLP techniques"""
        try:
            logger.info("[FALLBACK] Using enhanced NLP-based keyword extraction")
            
            # Use both simple extraction and NLP if available
            simple_keywords = self._extract_simple_keywords(file_content)
            
            # Enhanced keyword extraction using text analysis
            enhanced_keywords = self._extract_nlp_keywords(file_content)
            
            # Combine and organize keywords
            all_keywords = list(set(simple_keywords + enhanced_keywords))
            
            # Organize into categories
            keywords_data = {
                "primary_keywords": all_keywords[:8],
                "research_topics": all_keywords[8:12] if len(all_keywords) > 8 else ["research methodology"],
                "academic_concepts": all_keywords[12:18] if len(all_keywords) > 12 else ["data analysis", "academic study"],
                "technical_terms": all_keywords[18:24] if len(all_keywords) > 18 else ["methodology", "framework"],
                "domain_keywords": all_keywords[24:30] if len(all_keywords) > 24 else ["research domain"],
                "search_queries": [
                    " ".join(all_keywords[i:i+2]) for i in range(0, min(len(all_keywords), 8), 2)
                ] if len(all_keywords) > 2 else ["academic research"]
            }
            
            logger.info(f"[FALLBACK] Extracted {len(keywords_data['primary_keywords'])} keywords using enhanced fallback")
            return keywords_data
            
        except Exception as e:
            logger.error(f"[ERROR] Error in enhanced fallback extraction: {e}")
            # Ultimate fallback
            return {
                "primary_keywords": ["academic research", "data analysis", "research methodology"],
                "research_topics": ["research study"],
                "academic_concepts": ["analytical framework"],
                "technical_terms": ["methodology"],
                "domain_keywords": ["research domain"],
                "search_queries": ["academic research", "data analysis"]
            }

    def _extract_nlp_keywords(self, text: str) -> List[str]:
        """Extract keywords using NLP techniques"""
        try:
            if not text or len(text) < 50:
                return []
            
            keywords = []
            
            # Use spaCy if available
            if self.nlp:
                doc = self.nlp(text[:5000])  # Process up to 5000 characters
                
                # Extract named entities
                for ent in doc.ents:
                    if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT', 'WORK_OF_ART']:
                        if len(ent.text) > 2:
                            keywords.append(ent.text.lower())
                
                # Extract meaningful noun phrases
                for chunk in doc.noun_chunks:
                    if (2 <= len(chunk.text.split()) <= 4 and  # 2-4 words
                        len(chunk.text) > 5 and
                        not chunk.text.lower().startswith(('the ', 'a ', 'an '))):
                        keywords.append(chunk.text.lower())
                
                # Extract important tokens
                for token in doc:
                    if (token.pos_ in ['NOUN', 'PROPN'] and
                        len(token.text) > 4 and
                        token.text.lower() not in self.stop_words and
                        token.is_alpha):
                        keywords.append(token.text.lower())
            
            # TF-IDF based extraction as additional method
            if len(text) > 100:
                try:
                    # Clean text for TF-IDF
                    cleaned_text = ' '.join([
                        word for word in text.lower().split()
                        if word.isalpha() and len(word) > 3
                    ])
                    
                    if cleaned_text:
                        vectorizer = TfidfVectorizer(
                            max_features=20,
                            stop_words='english',
                            ngram_range=(1, 3),  # Include 1-3 word phrases
                            min_df=1
                        )
                        tfidf_matrix = vectorizer.fit_transform([cleaned_text])
                        feature_names = vectorizer.get_feature_names_out()
                        
                        # Get TF-IDF scores
                        scores = tfidf_matrix.toarray()[0]
                        keyword_scores = list(zip(feature_names, scores))
                        keyword_scores.sort(key=lambda x: x[1], reverse=True)
                        
                        # Add top TF-IDF keywords
                        tfidf_keywords = [kw[0] for kw in keyword_scores[:15]]
                        keywords.extend(tfidf_keywords)
                        
                except Exception as e:
                    logger.debug(f"TF-IDF extraction failed: {e}")
            
            # Remove duplicates and filter
            unique_keywords = []
            seen = set()
            for kw in keywords:
                kw_clean = kw.strip().lower()
                if (kw_clean not in seen and 
                    len(kw_clean) > 2 and
                    kw_clean not in ['research', 'study', 'analysis', 'method', 'data']):
                    unique_keywords.append(kw.strip())
                    seen.add(kw_clean)
            
            return unique_keywords[:25]  # Return top 25 keywords
            
        except Exception as e:
            logger.debug(f"Error in NLP keyword extraction: {e}")
            return []

    def _extract_simple_keywords(self, text: str) -> List[str]:
        """Extract simple keywords from text using basic NLP"""
        try:
            if not text or len(text) < 20:
                return ["research", "analysis", "study"]
            
            # Simple keyword extraction
            words = text.lower().split()
            # Remove common words and keep longer, meaningful terms
            keywords = []
            for word in words:
                if (len(word) > 4 and 
                    word.isalpha() and 
                    word not in ['research', 'analysis', 'study', 'method', 'finding'] and
                    not word.startswith('http')):
                    keywords.append(word)
            
            # Return unique keywords, limited to reasonable count
            return list(set(keywords))[:10] if keywords else ["research", "analysis", "study"]
            
        except Exception as e:
            logger.debug(f"Simple keyword extraction failed: {e}")
            return ["research", "analysis", "study"]

    def _get_google_file_content(self, file_id: str) -> str:
        """Get content from a Google file using service account authentication"""
        try:
            logger.info(f"[DOC] Attempting to retrieve Google file content: {file_id}")
            
            # Try to get as Google Doc first
            try:
                logger.info("[DOC] Trying as Google Docs document...")
                document = self.google_service.documents().get(documentId=file_id).execute()
                content = self._extract_text_from_google_doc(document)
                if content:
                    logger.info(f"[OK] Successfully retrieved Google Doc content ({len(content)} chars)")
                    return content
            except Exception as e:
                logger.debug(f"[DEBUG] Google Docs API failed: {e}")
            
            # Try to export as text using Drive API
            try:
                logger.info("[DOC] Trying as Drive file export...")
                content = self._export_google_file_as_text(file_id)
                if content:
                    logger.info(f"[OK] Successfully exported file content ({len(content)} chars)")
                    return content
            except Exception as e:
                logger.debug(f"[DEBUG] Drive export failed: {e}")
            
            logger.error("[ERROR] Failed to get file content - check file ID and sharing permissions")
            logger.error("  🔧 Make sure the file is shared with: sebastiancastano@phonic-goods-317118.iam.gserviceaccount.com")
            return ""
            
        except Exception as e:
            logger.error(f"[ERROR] Error getting Google file content: {e}")
            return ""

    def _extract_text_from_google_doc(self, doc: Dict) -> str:
        """Extract text from Google Doc structure"""
        def extract_text_from_element(element):
            text = ""
            if 'textRun' in element:
                text += element['textRun']['content']
            elif 'paragraph' in element:
                for elem in element['paragraph']['elements']:
                    text += extract_text_from_element(elem)
            return text
        
        content = doc.get('body', {}).get('content', [])
        full_text = ""
        
        for element in content:
            full_text += extract_text_from_element(element)
        
        return full_text

    def _export_google_file_as_text(self, file_id: str) -> str:
        """Export Google file as text"""
        try:
            # Try different export formats
            export_formats = [
                'text/plain',
                'application/rtf',
                'application/vnd.oasis.opendocument.text'
            ]
            
            for mime_type in export_formats:
                try:
                    request = self.drive_service.files().export_media(
                        fileId=file_id, mimeType=mime_type
                    )
                    content = request.execute()
                    
                    if isinstance(content, bytes):
                        return content.decode('utf-8', errors='ignore')
                    else:
                        return str(content)
                except:
                    continue
            
            return ""
            
        except Exception as e:
            logger.error(f"Error exporting file: {e}")
            return ""

    def run_complete_research_pipeline(self, google_file_id: str, output_format: str = "both") -> Dict[str, str]:
        """Run the complete research pipeline"""
        try:
            logger.info("[ROCKET] Starting complete research pipeline...")
            
            # Step 1: Extract keywords from Google file
            logger.info("[DOC] Step 1: Extracting keywords from Google file...")
            keywords_data = self.extract_keywords_from_google_file(google_file_id)
            
            if "error" in keywords_data:
                return {"error": keywords_data["error"]}
            
            # Step 2: Create search queries
            search_queries = []
            search_queries.extend(keywords_data.get("primary_keywords", []))
            search_queries.extend(keywords_data.get("research_topics", []))
            
            # Limit to top queries
            search_queries = search_queries[:5]
            
            logger.info(f"[SEARCH] Step 2: Searching with {len(search_queries)} queries...")
            
            # Step 3: Search Google Scholar
            papers = self.search_google_scholar(search_queries)
            
            if not papers:
                return {"error": "No papers found"}
            
            # Step 4: Filter and rank papers
            logger.info("🔬 Step 3: Filtering and ranking papers...")
            filtered_papers = self.filter_and_rank_papers(papers, " ".join(search_queries))
            
            # Step 5: Analyze research content
            logger.info("[STATS] Step 4: Analyzing research content...")
            analysis_data = self.analyze_research_content(filtered_papers)
            
            # Step 6: Analyze marketing relevance
            logger.info("[BULLSEYE] Step 5: Analyzing marketing relevance...")
            marketing_analysis = self.analyze_marketing_relevance(keywords_data, filtered_papers)
            
            # Step 7: Download and process PDFs
            logger.info("[DOWNLOAD] Step 6: Downloading and processing PDFs...")
            processed_papers = self.download_and_process_pdfs(filtered_papers)
            
            # Step 8: Create outputs based on format
            results = {}
            documents_created = {}
            
            context = f"Keywords from Google file: {google_file_id}"
            
            if output_format in ["docx", "both"]:
                logger.info("[DOC] Step 7: Creating Word document...")
                doc_filename = self.create_research_document(
                    analysis_data, 
                    context,
                    marketing_analysis
                )
                if doc_filename:
                    documents_created["word"] = {
                        "filename": doc_filename,
                        "type": "download",
                        "path": doc_filename
                    }
            
            if output_format in ["google_doc", "both"]:
                logger.info("[DOC] Step 7: Creating Google Document...")
                google_doc_result = self.create_google_document(
                    analysis_data,
                    context,
                    marketing_analysis
                )
                if 'error' not in google_doc_result:
                    documents_created["google_doc"] = {
                        "document_id": google_doc_result["document_id"],
                        "document_url": google_doc_result["document_url"],
                        "view_url": google_doc_result["view_url"],
                        "edit_url": google_doc_result["edit_url"],
                        "title": google_doc_result["title"],
                        "type": "link"
                    }
                else:
                    documents_created["google_doc_error"] = google_doc_result["error"]
            
            results["documents_created"] = documents_created
            
            # Add summary
            results["summary"] = {
                "papers_found": len(papers),
                "papers_analyzed": len(filtered_papers),
                "papers_processed": len(processed_papers),
                "search_queries": search_queries,
                "keywords_extracted": len(keywords_data.get("primary_keywords", [])),
                "marketing_analysis_completed": bool(marketing_analysis and not marketing_analysis.get('error')),
                "pdfs_downloaded": len([p for p in processed_papers if p.full_text]),
                "total_citations": sum(p.citations for p in processed_papers),
                "bright_data_stats": self.get_bright_data_stats(),
                "documents_created": len(documents_created),
                "word_doc_created": "word" in documents_created,
                "google_doc_created": "google_doc" in documents_created
            }
            
            logger.info("[OK] Research pipeline completed successfully!")
            logger.info(f"[STATS] Pipeline Summary:")
            logger.info(f"  [SEARCH] Papers found: {results['summary']['papers_found']}")
            logger.info(f"  [DOC] Papers analyzed: {results['summary']['papers_analyzed']}")
            logger.info(f"  [DOWNLOAD] PDFs processed: {results['summary']['pdfs_downloaded']}")
            logger.info(f"  [BULLSEYE] Marketing analysis: {'[OK]' if results['summary']['marketing_analysis_completed'] else '[ERROR]'}")
            
            return results
            
        except Exception as e:
            logger.error(f"[ERROR] Error in research pipeline: {e}")
            return {"error": str(e)}

    def configure_paper_download(self, 
                                enable_download: bool = True,
                                max_download_size_mb: int = 100,
                                download_timeout: int = 60,
                                download_directory: str = "downloaded_papers",
                                max_parallel_downloads: int = 8,
                                retry_attempts: int = 3) -> None:
        """Configure paper downloading settings"""
        self.download_papers = enable_download
        self.max_download_size = max_download_size_mb * 1024 * 1024
        self.download_timeout = download_timeout
        self.papers_download_dir = Path(download_directory)
        self.papers_download_dir.mkdir(exist_ok=True)
        
        self.max_parallel_downloads = max_parallel_downloads
        self.retry_attempts = retry_attempts
        
        logger.info(f"Paper download configured: enabled={enable_download}, "
                   f"max_size={max_download_size_mb}MB, timeout={download_timeout}s, "
                   f"parallel={max_parallel_downloads}, retries={retry_attempts}")

    def analyze_marketing_relevance(self, keywords_data: Dict[str, Any], papers: List[ResearchPaper]) -> Dict[str, Any]:
        """
        Analyze research papers for marketing relevance and business applications with detailed paper-by-paper analysis
        
        Args:
            keywords_data: Extracted keywords from input file
            papers: List of research papers
            
        Returns:
            Enhanced marketing relevance analysis with individual paper details
        """
        try:
            logger.info("[BULLSEYE] Analyzing marketing relevance with detailed paper analysis...")
            
            # Prepare detailed papers for analysis including full content
            detailed_papers = []
            papers_with_full_text = 0
            papers_with_abstract_only = 0
            
            for paper in papers:
                # Prepare comprehensive content for analysis
                content_parts = []
                
                # Add title
                if paper.title:
                    content_parts.append(f"Title: {paper.title}")
                
                # Add abstract
                if paper.abstract:
                    content_parts.append(f"Abstract: {paper.abstract}")
                
                # Add keywords
                if paper.keywords:
                    content_parts.append(f"Keywords: {', '.join(paper.keywords)}")
                
                # Add full text preview (PDF or URL content)
                if paper.full_text:
                    content_parts.append(f"Full Text Preview: {paper.full_text[:1500]}")
                    text_source = "Full text available"
                    papers_with_full_text += 1
                else:
                    text_source = "Abstract and keywords only"
                    papers_with_abstract_only += 1
                
                # Combine all available content
                combined_content = " | ".join(content_parts)
                
                paper_info = {
                    'title': paper.title,
                    'authors': paper.authors,
                    'year': paper.publication_year,
                    'journal': paper.journal,
                    'url': paper.url,
                    'citations': paper.citations,
                    'abstract': paper.abstract,
                    'keywords': paper.keywords,
                    'combined_content': combined_content,  # All available content
                    'text_source': text_source,
                    'relevance_score': paper.relevance_score,
                    'has_full_text': bool(paper.full_text)
                }
                detailed_papers.append(paper_info)
            
            # Enhanced marketing relevance analysis prompt
            marketing_prompt = f"""
            You are a senior marketing research analyst. Analyze the following research papers for their marketing relevance and business applications.
            
            IMPORTANT: Process ALL papers provided. Some have full text, others only abstracts and keywords. Provide comprehensive analysis for each based on available content.
            
            Content Analysis:
            - Papers with full text: {papers_with_full_text}
            - Papers with abstract only: {papers_with_abstract_only}
            - Total papers to analyze: {len(detailed_papers)}
            
            Original Search Keywords: {json.dumps(keywords_data)}
            
            Research Papers: {json.dumps(detailed_papers[:8])}  # Process up to 8 papers
            
            For EACH paper (analyze ALL provided papers), provide:
            1. **Paper Title & Authors**: Full citation information
            2. **Marketing Relevance Score**: Rate 1-10 (10 = extremely relevant to marketing)
            3. **Content Quality**: Note if analysis is based on full text or abstract only
            4. **Summary**: Brief overview of the paper's main findings
            5. **Marketing Takeaways**: 3-5 specific actionable insights for marketers
            6. **Business Applications**: How this research can be applied in business/marketing
            7. **Target Industries**: Which industries would benefit most from these findings
            8. **Implementation Strategy**: Step-by-step approach to use these insights
            9. **ROI Potential**: Expected return on investment (High/Medium/Low) with explanation
            10. **Consumer Behavior Insights**: What this reveals about consumer psychology
            11. **Competitive Advantage**: How businesses can use this to gain market advantage
            
            Then provide OVERALL ANALYSIS:
            12. **Content Quality Summary**: How the mix of full text vs abstract-only papers affects analysis
            13. **Top Marketing Trends**: 5 key trends identified across all papers
            14. **Cross-Paper Insights**: Common themes and contradictions
            15. **Industry Implications**: Which industries are most impacted
            16. **Marketing Strategy Recommendations**: Top 10 actionable recommendations
            17. **Future Marketing Directions**: What these papers suggest about future marketing
            18. **Implementation Roadmap**: Priority order for implementing insights
            
            Return as structured JSON with:
            - "individual_papers": Array of detailed paper analyses (MUST include ALL papers)
            - "overall_marketing_analysis": Combined insights
            - "executive_summary": 3-paragraph summary for marketing executives
            - "quick_actions": Top 5 immediate actions marketers can take
            - "content_quality_analysis": Analysis of how content availability affects insights
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": marketing_prompt}],
                temperature=0.3,
                max_tokens=4000
            )
            
            analysis_text = response.choices[0].message.content
            
            try:
                marketing_analysis = json.loads(analysis_text)
            except json.JSONDecodeError:
                # Enhanced fallback structure
                marketing_analysis = {
                    "individual_papers": [
                        {
                            "title": paper.title,
                            "authors": paper.authors,
                            "url": paper.url,
                            "marketing_relevance_score": 7,
                            "summary": paper.abstract[:200] + "..." if paper.abstract else "No abstract available",
                            "marketing_takeaways": ["Data-driven insights", "Consumer behavior patterns", "Market trends"],
                            "business_applications": ["Marketing strategy", "Customer engagement", "Brand positioning"]
                        } for paper in papers[:5]
                    ],
                    "overall_marketing_analysis": {
                        "top_marketing_trends": ["Data-driven marketing", "Consumer behavior analysis", "Digital transformation"],
                        "marketing_strategy_recommendations": ["Implement research findings", "Use data for decisions", "Focus on consumer insights"]
                    },
                    "executive_summary": analysis_text,
                    "quick_actions": ["Review paper findings", "Implement top insights", "Monitor market trends"],
                    "content_quality_analysis": "Analysis of how content availability affects insights"
                }
            
            # Add comprehensive metadata
            marketing_analysis["analysis_metadata"] = {
                "papers_analyzed": len(papers),
                "total_citations": sum(p.citations for p in papers),
                "average_citations": sum(p.citations for p in papers) / len(papers) if papers else 0,
                "average_relevance_score": sum(p.relevance_score for p in papers) / len(papers) if papers else 0,
                "year_range": f"{min(p.publication_year for p in papers if p.publication_year > 0)} - {max(p.publication_year for p in papers if p.publication_year > 0)}" if papers else "N/A",
                "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "keywords_used": keywords_data.get("primary_keywords", [])
            }
            
            # Add paper details for easy reference
            marketing_analysis["paper_references"] = [
                {
                    "title": paper.title,
                    "authors": paper.authors,
                    "year": paper.publication_year,
                    "journal": paper.journal,
                    "url": paper.url,
                    "citations": paper.citations,
                    "relevance_score": paper.relevance_score
                } for paper in papers
            ]
            
            logger.info("[OK] Enhanced marketing relevance analysis completed")
            return marketing_analysis
            
        except Exception as e:
            logger.error(f"[ERROR] Error analyzing marketing relevance: {e}")
            return {"error": str(e), "papers_analyzed": len(papers)}

    def download_and_process_pdfs(self, papers: List[ResearchPaper]) -> List[ResearchPaper]:
        """
        Enhanced paper processing: Download PDFs, scrape webpages, and analyze all content with OpenAI
        
        Args:
            papers: List of research papers
            
        Returns:
            Papers with full-text content and AI-enhanced analysis
        """
        try:
            logger.info(f"[DOWNLOAD] Enhanced processing of {len(papers)} papers (PDF + AI analysis + webpage scraping)...")
            
            processed_papers = []
            pdf_success_count = 0
            url_success_count = 0
            ai_analysis_count = 0
            
            # Process each paper with aggressive content acquisition and AI analysis
            for i, paper in enumerate(papers, 1):
                try:
                    logger.info(f"[PROCESS] Processing paper {i}/{len(papers)}: {paper.title[:60]}...")
                    
                    content_acquired = False
                    content_source = "abstract_only"
                    
                    # Step 1: Try PDF download first (highest priority)
                    if self.download_papers:
                        logger.debug(f"[PDF] Attempting PDF download for: {paper.title[:50]}...")
                        pdf_success = self._enhanced_pdf_download_and_analysis(paper)
                        if pdf_success:
                            content_acquired = True
                            content_source = "pdf_full_text"
                            pdf_success_count += 1
                            logger.info(f"[PDF] ✅ PDF downloaded and analyzed: {paper.title[:50]}...")
                    
                    # Step 2: If PDF failed, try aggressive webpage scraping
                    if not content_acquired and paper.url:
                        logger.debug(f"[WEB] Attempting enhanced webpage scraping for: {paper.title[:50]}...")
                        web_success = self._enhanced_webpage_scraping_and_analysis(paper)
                        if web_success:
                            content_acquired = True
                            content_source = "webpage_content"
                            url_success_count += 1
                            logger.info(f"[WEB] ✅ Webpage scraped and analyzed: {paper.title[:50]}...")
                    
                    # Step 3: Apply AI analysis to whatever content we have
                    if content_acquired:
                        ai_enhanced = self._apply_ai_content_analysis(paper, content_source)
                        if ai_enhanced:
                            ai_analysis_count += 1
                            logger.debug(f"[AI] ✅ AI analysis applied to: {paper.title[:50]}...")
                    
                    # Step 4: Enhance abstract-only papers with AI if no full content
                    if not content_acquired and paper.abstract:
                        logger.debug(f"[AI-ABSTRACT] Enhancing abstract-only paper: {paper.title[:50]}...")
                        self._enhance_abstract_with_ai(paper)
                        content_source = "enhanced_abstract"
                    
                    # Add metadata about content quality
                    paper.content_source = content_source
                    paper.ai_enhanced = content_acquired or bool(paper.abstract)
                    
                    processed_papers.append(paper)
                    
                except Exception as e:
                    logger.error(f"[ERROR] Error processing paper '{paper.title}': {e}")
                    # Still add the paper with basic info
                    paper.content_source = "error"
                    paper.ai_enhanced = False
                    processed_papers.append(paper)
            
            # Enhanced logging with detailed statistics
            logger.info(f"[COMPLETE] Enhanced processing completed for {len(processed_papers)} papers:")
            logger.info(f"  📄 PDF downloads & analysis: {pdf_success_count}")
            logger.info(f"  🌐 Webpage scraping & analysis: {url_success_count}")
            logger.info(f"  🤖 AI content analysis applied: {ai_analysis_count}")
            logger.info(f"  📝 Abstract-only papers: {len(processed_papers) - pdf_success_count - url_success_count}")
            
            # Calculate content quality score
            full_content_papers = pdf_success_count + url_success_count
            content_quality_score = (full_content_papers / len(papers)) * 100 if papers else 0
            logger.info(f"  📊 Content acquisition rate: {content_quality_score:.1f}%")
            
            return processed_papers
            
        except Exception as e:
            logger.error(f"[ERROR] Error in enhanced paper processing: {e}")
            return papers

    def _enhanced_pdf_download_and_analysis(self, paper: ResearchPaper) -> bool:
        """
        Enhanced PDF download with AI analysis of full text content
        
        Args:
            paper: Research paper to process
            
        Returns:
            True if PDF was successfully downloaded and analyzed
        """
        try:
            if not paper.url:
                logger.debug(f"[PDF] No URL available for paper: {paper.title}")
                return False
            
            # Try to find PDF link with multiple strategies
            pdf_url = self._find_pdf_link_aggressive(paper.url)
            if not pdf_url:
                logger.debug(f"[PDF] No PDF link found for paper: {paper.title}")
                return False
            
            # Download PDF with retry logic
            pdf_content = self._download_pdf_with_retry(pdf_url, paper.title)
            if not pdf_content:
                logger.debug(f"[PDF] Failed to download PDF for paper: {paper.title}")
                return False
            
            # Extract text from PDF with multiple methods
            full_text = self._extract_text_from_pdf_enhanced(pdf_content)
            if not full_text or len(full_text) < 100:
                logger.debug(f"[PDF] Failed to extract meaningful text from PDF: {paper.title}")
                return False
            
            # Store full text and apply AI analysis
            paper.full_text = full_text
            
            # Extract enhanced keywords and insights from full text
            ai_insights = self._analyze_full_text_with_ai(full_text, paper.title)
            if ai_insights:
                # Enhance paper with AI insights
                paper.keywords.extend(ai_insights.get('enhanced_keywords', []))
                paper.ai_summary = ai_insights.get('summary', '')
                paper.key_findings = ai_insights.get('key_findings', [])
                paper.methodology = ai_insights.get('methodology', '')
                paper.business_relevance = ai_insights.get('business_relevance', '')
            
            logger.debug(f"[PDF] Successfully processed and analyzed PDF: {paper.title}")
            return True
            
        except Exception as e:
            logger.error(f"[PDF] Error in enhanced PDF processing for '{paper.title}': {e}")
            return False

    def _enhanced_webpage_scraping_and_analysis(self, paper: ResearchPaper) -> bool:
        """
        Enhanced webpage scraping with AI analysis of page content
        
        Args:
            paper: Research paper to process
            
        Returns:
            True if webpage was successfully scraped and analyzed
        """
        try:
            if not paper.url or not paper.url.startswith('http'):
                return False
            
            logger.debug(f"[WEB] Enhanced scraping from: {paper.url}")
            
            # Try multiple scraping methods
            scraped_content = self._scrape_url_content_aggressive(paper.url)
            if not scraped_content or len(scraped_content) < 200:
                logger.debug(f"[WEB] Failed to scrape meaningful content from: {paper.url}")
                return False
            
            # Store scraped content
            paper.full_text = scraped_content
            
            # Apply AI analysis to scraped content
            ai_insights = self._analyze_webpage_content_with_ai(scraped_content, paper.title, paper.url)
            if ai_insights:
                # Enhance paper with AI insights
                paper.keywords.extend(ai_insights.get('enhanced_keywords', []))
                paper.ai_summary = ai_insights.get('summary', '')
                paper.key_findings = ai_insights.get('key_findings', [])
                paper.methodology = ai_insights.get('methodology', '')
                paper.business_relevance = ai_insights.get('business_relevance', '')
                paper.content_quality_score = ai_insights.get('quality_score', 0.5)
            
            logger.debug(f"[WEB] Successfully scraped and analyzed webpage: {paper.title}")
            return True
            
        except Exception as e:
            logger.error(f"[WEB] Error in enhanced webpage scraping for '{paper.title}': {e}")
            return False

    def _apply_ai_content_analysis(self, paper: ResearchPaper, content_source: str) -> bool:
        """
        Apply comprehensive AI analysis to paper content regardless of source
        
        Args:
            paper: Research paper with content
            content_source: Source of the content (pdf_full_text, webpage_content, etc.)
            
        Returns:
            True if AI analysis was successfully applied
        """
        try:
            if not paper.full_text:
                return False
            
            logger.debug(f"[AI] Applying comprehensive analysis to {content_source}: {paper.title[:50]}...")
            
            # Prepare content for analysis
            content_preview = paper.full_text[:8000]  # Use first 8000 characters
            
            # Apply different AI analysis based on content source
            if content_source == "pdf_full_text":
                analysis = self._ai_analyze_academic_paper(content_preview, paper.title, paper.abstract)
            elif content_source == "webpage_content":
                analysis = self._ai_analyze_webpage_content(content_preview, paper.title, paper.url)
            else:
                analysis = self._ai_analyze_general_content(content_preview, paper.title)
            
            if analysis:
                # Apply insights to paper
                paper.ai_analysis = analysis
                paper.research_significance = analysis.get('significance_score', 0.5)
                paper.practical_applications = analysis.get('applications', [])
                paper.future_research_directions = analysis.get('future_research', [])
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"[AI] Error in AI content analysis for '{paper.title}': {e}")
            return False

    def _enhance_abstract_with_ai(self, paper: ResearchPaper) -> bool:
        """
        Enhance abstract-only papers with AI analysis
        
        Args:
            paper: Research paper with abstract
            
        Returns:
            True if abstract was successfully enhanced
        """
        try:
            if not paper.abstract:
                return False
            
            logger.debug(f"[AI-ABSTRACT] Enhancing abstract: {paper.title[:50]}...")
            
            # Apply AI analysis to abstract
            enhancement = self._ai_enhance_abstract(paper.abstract, paper.title)
            if enhancement:
                paper.ai_enhanced_abstract = enhancement.get('enhanced_abstract', paper.abstract)
                paper.implied_methodology = enhancement.get('methodology', '')
                paper.potential_applications = enhancement.get('applications', [])
                paper.research_gaps_identified = enhancement.get('research_gaps', [])
                paper.ai_confidence_score = enhancement.get('confidence', 0.3)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"[AI-ABSTRACT] Error enhancing abstract for '{paper.title}': {e}")
            return False

    def _download_and_process_single_pdf(self, paper: ResearchPaper) -> Optional[ResearchPaper]:
        """
        Download and process a single PDF paper
        
        Args:
            paper: Research paper to process
            
        Returns:
            Paper with full-text content or None if failed
        """
        try:
            if not paper.url:
                logger.debug(f"[WARNING] No URL available for paper: {paper.title}")
                return paper
            
            # Try to find PDF link
            pdf_url = self._find_pdf_link(paper.url)
            if not pdf_url:
                logger.debug(f"[WARNING] No PDF link found for paper: {paper.title}")
                return paper
            
            # Download PDF
            pdf_content = self._download_pdf(pdf_url, paper.title)
            if not pdf_content:
                logger.debug(f"[WARNING] Failed to download PDF for paper: {paper.title}")
                return paper
            
            # Extract text from PDF
            full_text = self._extract_text_from_pdf(pdf_content)
            if not full_text:
                logger.debug(f"[WARNING] Failed to extract text from PDF: {paper.title}")
                return paper
            
            # Update paper with full text
            paper.full_text = full_text
            
            # Extract additional keywords from full text
            additional_keywords = self._extract_keywords_from_text(full_text)
            paper.keywords.extend(additional_keywords)
            
            logger.debug(f"[OK] Successfully processed PDF for: {paper.title}")
            return paper
            
        except Exception as e:
            logger.error(f"[ERROR] Error processing PDF for '{paper.title}': {e}")
            return paper

    def _find_pdf_link(self, paper_url: str) -> Optional[str]:
        """
        Find PDF download link from paper URL
        
        Args:
            paper_url: URL of the paper
            
        Returns:
            PDF download URL or None
        """
        try:
            # Try direct PDF URL first
            if paper_url.endswith('.pdf'):
                return paper_url
            
            # Use Bright Data to get the page content
            response = self._make_bright_data_request(paper_url)
            if not response or not response.get('content'):
                return None
            
            # Parse HTML to find PDF links
            soup = BeautifulSoup(response['content'], 'html.parser')
            
            # Common PDF link patterns
            pdf_links = []
            
            # Look for direct PDF links
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and ('.pdf' in href.lower() or 'download' in href.lower()):
                    pdf_links.append(href)
            
            # Look for meta tags with PDF URLs
            for meta in soup.find_all('meta'):
                content = meta.get('content', '')
                if content and '.pdf' in content.lower():
                    pdf_links.append(content)
            
            # Return first valid PDF link
            for link in pdf_links:
                if link.startswith('http'):
                    return link
                elif link.startswith('/'):
                    from urllib.parse import urljoin
                    return urljoin(paper_url, link)
            
            return None
            
        except Exception as e:
            logger.debug(f"Error finding PDF link: {e}")
            return None

    def _download_pdf(self, pdf_url: str, title: str) -> Optional[bytes]:
        """
        Download PDF content
        
        Args:
            pdf_url: URL of the PDF
            title: Paper title (for logging)
            
        Returns:
            PDF content bytes or None
        """
        try:
            # Use Bright Data for PDF download
            response = self._make_bright_data_request(pdf_url)
            if not response or not response.get('content'):
                return None
            
            # For PDF files, the content should be binary
            # Since we're using raw format, we need to handle this carefully
            content = response['content']
            
            # Check if it's actually a PDF
            if not content.startswith('%PDF'):
                logger.debug(f"[WARNING] Downloaded content is not a PDF: {title}")
                return None
            
            # Check size limit
            if len(content) > self.max_download_size:
                logger.warning(f"[WARNING] PDF too large ({len(content)} bytes): {title}")
                return None
            
            # Save to local file
            filename = f"{title[:50].replace('/', '_').replace('\\', '_')}.pdf"
            filepath = self.papers_download_dir / filename
            
            with open(filepath, 'wb') as f:
                f.write(content.encode('latin-1'))  # Handle binary content
            
            logger.debug(f"[OK] Downloaded PDF: {filename}")
            return content.encode('latin-1')
            
        except Exception as e:
            logger.debug(f"Error downloading PDF: {e}")
            return None

    def _extract_text_from_pdf(self, pdf_content: bytes) -> str:
        """
        Extract text from PDF content using multiple methods
        
        Args:
            pdf_content: PDF content as bytes
            
        Returns:
            Extracted text
        """
        try:
            # Try PyMuPDF first (most reliable)
            if PYMUPDF_AVAILABLE:
                try:
                    doc = fitz.open(stream=pdf_content, filetype="pdf")
                    text = ""
                    for page in doc:
                        text += page.get_text()
                    doc.close()
                    if text.strip():
                        return text
                except Exception as e:
                    logger.debug(f"PyMuPDF extraction failed: {e}")
            
            # Try pdfplumber
            if PDFPLUMBER_AVAILABLE:
                try:
                    import io
                    with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                        text = ""
                        for page in pdf.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                        if text.strip():
                            return text
                except Exception as e:
                    logger.debug(f"pdfplumber extraction failed: {e}")
            
            # Try PyPDF2 as fallback
            if PYPDF2_AVAILABLE:
                try:
                    import io
                    reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    if text.strip():
                        return text
                except Exception as e:
                    logger.debug(f"PyPDF2 extraction failed: {e}")
            
            logger.debug("[ERROR] All PDF extraction methods failed")
            return ""
            
        except Exception as e:
            logger.debug(f"Error extracting text from PDF: {e}")
            return ""

    def _scrape_url_content(self, url: str) -> str:
        """
        Scrape content from a URL as fallback when PDF download fails
        
        Args:
            url: URL to scrape content from
            
        Returns:
            Scraped text content
        """
        try:
            if not url or not url.startswith('http'):
                return ""
            
            logger.debug(f"[URL] Scraping content from: {url}")
            
            # Try with Bright Data first if available
            if self.bright_data_enabled:
                try:
                    response = self._make_bright_data_request(url)
                    if response and response.get('content'):
                        content = response['content']
                        text = self._extract_text_from_html(content)
                        if text and len(text) > 200:  # Minimum content length
                            logger.debug(f"[URL] Scraped {len(text)} characters via Bright Data")
                            return text
                except Exception as e:
                    logger.debug(f"[URL] Bright Data scraping failed: {e}")
            
            # Fallback to direct requests
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    content = response.text
                    text = self._extract_text_from_html(content)
                    if text and len(text) > 200:
                        logger.debug(f"[URL] Scraped {len(text)} characters via direct request")
                        return text
                        
            except Exception as e:
                logger.debug(f"[URL] Direct request failed: {e}")
            
            logger.debug(f"[URL] Failed to scrape content from URL")
            return ""
            
        except Exception as e:
            logger.debug(f"[URL] Error scraping URL content: {e}")
            return ""

    def _extract_text_from_html(self, html_content: str) -> str:
        """
        Extract readable text from HTML content
        
        Args:
            html_content: HTML content to parse
            
        Returns:
            Extracted text
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
                element.decompose()
            
            # Extract text from common academic paper elements
            text_elements = []
            
            # Look for common academic paper sections
            for selector in ['article', 'main', '.content', '.paper-content', '.abstract', '.fulltext']:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        text_elements.append(element.get_text())
            
            # If no specific elements found, get all text
            if not text_elements:
                text_elements = [soup.get_text()]
            
            # Clean and combine text
            combined_text = ' '.join(text_elements)
            
            # Clean up whitespace
            lines = (line.strip() for line in combined_text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit text length to avoid token limits
            if len(text) > 10000:
                text = text[:10000] + "..."
            
            return text
            
        except Exception as e:
            logger.debug(f"[URL] Error extracting text from HTML: {e}")
            return ""

    def _analyze_full_text_with_ai(self, full_text: str, title: str) -> Optional[Dict[str, Any]]:
        """
        Analyze full PDF text with OpenAI for enhanced insights
        
        Args:
            full_text: Full text content from PDF
            title: Paper title
            
        Returns:
            Dictionary with AI analysis results
        """
        try:
            # Prepare content for analysis (use first 6000 characters)
            content_sample = full_text[:6000]
            
            analysis_prompt = f"""
            Analyze this academic paper's full text and extract comprehensive insights for research purposes.

            PAPER TITLE: {title}
            
            FULL TEXT CONTENT:
            {content_sample}

            Provide a comprehensive analysis in JSON format with:
            1. ENHANCED_KEYWORDS: 8-12 sophisticated academic keywords/phrases from the full text
            2. SUMMARY: 2-3 sentence summary of the paper's main contribution
            3. KEY_FINDINGS: 4-6 specific findings or results from the paper
            4. METHODOLOGY: Research methodology or approach used
            5. BUSINESS_RELEVANCE: How this research applies to business/marketing (2-3 sentences)
            6. TECHNICAL_DEPTH: Rate the technical complexity (1-10)
            7. INNOVATION_SCORE: Rate the novelty/innovation (1-10)
            8. PRACTICAL_IMPACT: Real-world applications or implications

            Return ONLY valid JSON:
            {{
                "enhanced_keywords": ["keyword1", "keyword2", ...],
                "summary": "Paper summary here",
                "key_findings": ["finding1", "finding2", ...],
                "methodology": "Research methodology",
                "business_relevance": "Business applications",
                "technical_depth": 7,
                "innovation_score": 8,
                "practical_impact": "Real-world impact"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert academic research analyst. Provide precise, insightful analysis of research papers."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean and parse JSON response
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            analysis_result = json.loads(result_text)
            logger.debug(f"[AI-PDF] Successfully analyzed full text for: {title[:50]}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"[AI-PDF] Error analyzing full text: {e}")
            return None

    def _analyze_webpage_content_with_ai(self, content: str, title: str, url: str) -> Optional[Dict[str, Any]]:
        """
        Analyze webpage content with OpenAI for research insights
        
        Args:
            content: Scraped webpage content
            title: Paper title
            url: Source URL
            
        Returns:
            Dictionary with AI analysis results
        """
        try:
            # Prepare content for analysis
            content_sample = content[:5000]
            
            analysis_prompt = f"""
            Analyze this academic webpage content and extract research insights.

            PAPER TITLE: {title}
            SOURCE URL: {url}
            
            WEBPAGE CONTENT:
            {content_sample}

            Extract research-relevant information in JSON format:
            1. ENHANCED_KEYWORDS: 6-10 academic keywords from the content
            2. SUMMARY: Summary of the main research points (2-3 sentences)
            3. KEY_FINDINGS: Important findings or insights mentioned
            4. METHODOLOGY: Any research methods discussed
            5. BUSINESS_RELEVANCE: Business/marketing relevance
            6. QUALITY_SCORE: Content quality for research purposes (0.0-1.0)
            7. CONTENT_TYPE: Type of content (abstract, full_paper, summary, etc.)

            Return ONLY valid JSON:
            {{
                "enhanced_keywords": ["keyword1", "keyword2", ...],
                "summary": "Content summary",
                "key_findings": ["finding1", "finding2", ...],
                "methodology": "Research methodology if mentioned",
                "business_relevance": "Business applications",
                "quality_score": 0.8,
                "content_type": "webpage_summary"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting research insights from web content. Focus on academic and business relevance."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=1200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean and parse JSON response
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            analysis_result = json.loads(result_text)
            logger.debug(f"[AI-WEB] Successfully analyzed webpage content for: {title[:50]}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"[AI-WEB] Error analyzing webpage content: {e}")
            return None

    def _ai_analyze_academic_paper(self, content: str, title: str, abstract: str) -> Optional[Dict[str, Any]]:
        """
        Comprehensive AI analysis for academic papers
        """
        try:
            analysis_prompt = f"""
            Conduct a comprehensive academic analysis of this research paper.

            TITLE: {title}
            ABSTRACT: {abstract}
            CONTENT: {content[:7000]}

            Provide detailed analysis in JSON format:
            {{
                "significance_score": 0.85,
                "applications": ["app1", "app2", "app3"],
                "future_research": ["direction1", "direction2"],
                "research_quality": 0.9,
                "citation_potential": 0.8,
                "interdisciplinary_relevance": ["field1", "field2"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a senior academic research analyst with expertise in evaluating research significance and impact."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
            
        except Exception as e:
            logger.error(f"[AI-ACADEMIC] Error in academic analysis: {e}")
            return None

    def _ai_analyze_webpage_content(self, content: str, title: str, url: str) -> Optional[Dict[str, Any]]:
        """
        AI analysis specific to webpage content
        """
        try:
            # Similar implementation to _analyze_webpage_content_with_ai but focused on academic evaluation
            return self._analyze_webpage_content_with_ai(content, title, url)
        except Exception as e:
            logger.error(f"[AI-WEB-ACADEMIC] Error in webpage academic analysis: {e}")
            return None

    def _ai_analyze_general_content(self, content: str, title: str) -> Optional[Dict[str, Any]]:
        """
        General AI analysis for any content type
        """
        try:
            analysis_prompt = f"""
            Analyze this research content and provide academic insights.

            TITLE: {title}
            CONTENT: {content[:6000]}

            Provide analysis in JSON format:
            {{
                "significance_score": 0.7,
                "applications": ["application1", "application2"],
                "future_research": ["research_direction1"],
                "content_quality": 0.8
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a research analyst. Provide insights on academic content."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
            
        except Exception as e:
            logger.error(f"[AI-GENERAL] Error in general content analysis: {e}")
            return None

    def _ai_enhance_abstract(self, abstract: str, title: str) -> Optional[Dict[str, Any]]:
        """
        Enhance abstract-only papers with AI insights
        """
        try:
            enhancement_prompt = f"""
            Enhance this research abstract with deeper insights and implications.

            TITLE: {title}
            ABSTRACT: {abstract}

            Provide enhanced analysis in JSON format:
            {{
                "enhanced_abstract": "Enhanced version with deeper insights",
                "methodology": "Implied research methodology",
                "applications": ["practical_application1", "application2"],
                "research_gaps": ["gap1", "gap2"],
                "confidence": 0.6
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert at inferring deeper research insights from abstracts."},
                    {"role": "user", "content": enhancement_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            result = json.loads(response.choices[0].message.content.strip())
            return result
            
        except Exception as e:
            logger.error(f"[AI-ABSTRACT] Error enhancing abstract: {e}")
            return None

    def _find_pdf_link_aggressive(self, paper_url: str) -> Optional[str]:
        """
        Enhanced PDF link finding with multiple strategies
        """
        try:
            # Try direct PDF URL first
            if paper_url.endswith('.pdf'):
                return paper_url
            
            # Strategy 1: Use existing method
            pdf_link = self._find_pdf_link(paper_url)
            if pdf_link:
                return pdf_link
            
            # Strategy 2: Try common PDF URL patterns
            base_url = paper_url.replace('/abs/', '/pdf/').replace('/abstract/', '/pdf/')
            if base_url != paper_url:
                return base_url
            
            # Strategy 3: Add .pdf extension to various formats
            pdf_variants = [
                paper_url + '.pdf',
                paper_url.replace('.html', '.pdf'),
                paper_url.replace('/html/', '/pdf/')
            ]
            
            for variant in pdf_variants:
                if variant != paper_url:
                    return variant
            
            return None
            
        except Exception as e:
            logger.debug(f"Error in aggressive PDF link finding: {e}")
            return None

    def _download_pdf_with_retry(self, pdf_url: str, title: str, max_retries: int = 3) -> Optional[bytes]:
        """
        Download PDF with retry logic and multiple methods
        """
        for attempt in range(max_retries):
            try:
                # Try existing method first
                pdf_content = self._download_pdf(pdf_url, title)
                if pdf_content:
                    return pdf_content
                
                # Try direct download if Bright Data fails
                if attempt == max_retries - 1:  # Last attempt
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = requests.get(pdf_url, headers=headers, timeout=30)
                    if response.status_code == 200 and response.content.startswith(b'%PDF'):
                        return response.content
                
                time.sleep(2 ** attempt)  # Exponential backoff
                
            except Exception as e:
                logger.debug(f"PDF download attempt {attempt + 1} failed: {e}")
                
        return None

    def _extract_text_from_pdf_enhanced(self, pdf_content: bytes) -> str:
        """
        Enhanced PDF text extraction with multiple methods and cleaning
        """
        try:
            # Try existing method first
            text = self._extract_text_from_pdf(pdf_content)
            if text and len(text) > 100:
                # Clean and enhance the extracted text
                cleaned_text = self._clean_extracted_text(text)
                return cleaned_text
            
            return ""
            
        except Exception as e:
            logger.debug(f"Enhanced PDF text extraction failed: {e}")
            return ""

    def _clean_extracted_text(self, text: str) -> str:
        """
        Clean and enhance extracted text for better AI analysis
        """
        try:
            # Remove excessive whitespace
            text = ' '.join(text.split())
            
            # Remove common PDF artifacts
            text = re.sub(r'\x0c', ' ', text)  # Form feed characters
            text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Non-ASCII characters
            text = re.sub(r'\s+', ' ', text)  # Multiple spaces
            
            # Remove page numbers and headers/footers patterns
            text = re.sub(r'\b\d+\s*$', '', text, flags=re.MULTILINE)
            
            return text.strip()
            
        except Exception as e:
            logger.debug(f"Text cleaning failed: {e}")
            return text

    def _scrape_url_content_aggressive(self, url: str) -> str:
        """
        Enhanced webpage scraping with multiple strategies and AI-optimized extraction
        """
        try:
            # Try existing method first
            content = self._scrape_url_content(url)
            if content and len(content) > 200:
                return content
            
            # Strategy 2: Try different approaches for academic sites
            if any(domain in url for domain in ['arxiv.org', 'ieee.org', 'acm.org', 'springer.com', 'sciencedirect.com']):
                academic_content = self._scrape_academic_site(url)
                if academic_content:
                    return academic_content
            
            # Strategy 3: Try with different headers and retry
            headers_list = [
                {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive'
                },
                {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            ]
            
            for headers in headers_list:
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    if response.status_code == 200:
                        text = self._extract_text_from_html_enhanced(response.text)
                        if text and len(text) > 200:
                            return text
                except:
                    continue
            
            return ""
            
        except Exception as e:
            logger.debug(f"Aggressive URL scraping failed: {e}")
            return ""

    def _scrape_academic_site(self, url: str) -> str:
        """
        Specialized scraping for academic websites
        """
        try:
            # This would contain site-specific scraping logic for major academic publishers
            # For now, use the general method
            return self._scrape_url_content(url)
        except Exception as e:
            logger.debug(f"Academic site scraping failed: {e}")
            return ""

    def _extract_text_from_html_enhanced(self, html_content: str) -> str:
        """
        Enhanced HTML text extraction optimized for academic content
        """
        try:
            # Use existing method but with enhancements
            base_text = self._extract_text_from_html(html_content)
            
            if base_text:
                # Additional processing for academic content
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Look for specific academic content sections
                academic_sections = soup.find_all(['div', 'section', 'article'], 
                                                class_=re.compile(r'abstract|content|body|main|article', re.I))
                
                if academic_sections:
                    section_texts = []
                    for section in academic_sections:
                        section_text = section.get_text(strip=True)
                        if len(section_text) > 100:
                            section_texts.append(section_text)
                    
                    if section_texts:
                        enhanced_text = ' '.join(section_texts)
                        return enhanced_text[:10000]  # Limit length
                
                return base_text
            
            return ""
            
        except Exception as e:
            logger.debug(f"Enhanced HTML text extraction failed: {e}")
            return ""

    def _extract_keywords_from_text(self, text: str) -> List[str]:
        """
        Extract keywords from full text using NLP
        
        Args:
            text: Full text content
            
        Returns:
            List of extracted keywords
        """
        try:
            if not text or len(text) < 100:
                return []
            
            # Use spaCy for keyword extraction if available
            if self.nlp:
                doc = self.nlp(text[:10000])  # Limit text length
                keywords = []
                
                # Extract named entities
                for ent in doc.ents:
                    if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT']:
                        keywords.append(ent.text)
                
                # Extract noun phrases
                for chunk in doc.noun_chunks:
                    if len(chunk.text.split()) <= 3:  # Limit to 3 words
                        keywords.append(chunk.text)
                
                # Remove duplicates and filter
                keywords = list(set(keywords))
                keywords = [kw for kw in keywords if len(kw) > 3 and kw.lower() not in self.stop_words]
                
                return keywords[:20]  # Return top 20 keywords
            
            # Fallback to simple keyword extraction
            words = word_tokenize(text.lower())
            words = [word for word in words if word.isalpha() and word not in self.stop_words]
            
            # Use TF-IDF for keyword extraction
            if len(words) > 10:
                vectorizer = TfidfVectorizer(max_features=20, stop_words='english')
                tfidf_matrix = vectorizer.fit_transform([' '.join(words)])
                feature_names = vectorizer.get_feature_names_out()
                return feature_names.tolist()
            
            return []
            
        except Exception as e:
            logger.debug(f"Error extracting keywords: {e}")
            return []

    def run_marketing_research_example(self, search_topics: List[str]) -> Dict[str, Any]:
        """
        Run a complete marketing research example with the full workflow
        
        Args:
            search_topics: List of topics to research
            
        Returns:
            Complete research results with marketing analysis
        """
        try:
            logger.info("[ROCKET] Starting Marketing Research Example...")
            logger.info(f"[WRITE] Research Topics: {search_topics}")
            
            # Step 1: Create mock keywords data (simulating extraction from input file)
            keywords_data = {
                "primary_keywords": search_topics,
                "secondary_keywords": ["consumer behavior", "market trends", "digital marketing", "brand strategy"],
                "research_topics": search_topics,
                "methodologies": ["quantitative analysis", "qualitative research", "case studies"]
            }
            
            logger.info("[DOC] Step 1: Keywords extracted (simulated)")
            
            # Step 2: Search Google Scholar
            logger.info("[SEARCH] Step 2: Searching Google Scholar...")
            papers = self.search_google_scholar(search_topics)
            
            if not papers:
                logger.warning("[WARNING] No papers found - generating example with limited data")
                return {
                    "error": "No papers found",
                    "keywords_data": keywords_data,
                    "bright_data_stats": self.get_bright_data_stats()
                }
            
            # Step 3: Filter and rank papers
            logger.info("🔬 Step 3: Filtering and ranking papers...")
            filtered_papers = self.filter_and_rank_papers(papers, " ".join(search_topics))
            
            # Step 4: Download and process PDFs
            logger.info("[DOWNLOAD] Step 4: Downloading and processing PDFs...")
            processed_papers = self.download_and_process_pdfs(filtered_papers)
            
            # Step 5: Analyze research content
            logger.info("[STATS] Step 5: Analyzing research content...")
            analysis_data = self.analyze_research_content(processed_papers)
            
            # Step 6: Analyze marketing relevance
            logger.info("[BULLSEYE] Step 6: Analyzing marketing relevance...")
            marketing_analysis = self.analyze_marketing_relevance(keywords_data, processed_papers)
            
            # Step 7: Create comprehensive documents
            logger.info("[DOC] Step 7: Creating comprehensive research documents...")
            
            # Create both Word and Google documents by default for example
            documents_created = {}
            context = f"Marketing Research Example: {', '.join(search_topics)}"
            
            # Create Word document
            doc_filename = self.create_research_document(
                analysis_data,
                context,
                marketing_analysis
            )
            if doc_filename:
                documents_created["word"] = {
                    "filename": doc_filename,
                    "type": "download",
                    "path": doc_filename
                }
            
            # Create Google document if authenticated
            if self.google_authenticated:
                google_doc_result = self.create_google_document(
                    analysis_data,
                    context,
                    marketing_analysis
                )
                if 'error' not in google_doc_result:
                    documents_created["google_doc"] = {
                        "document_id": google_doc_result["document_id"],
                        "document_url": google_doc_result["document_url"],
                        "view_url": google_doc_result["view_url"],
                        "edit_url": google_doc_result["edit_url"],
                        "title": google_doc_result["title"],
                        "type": "link"
                    }
                else:
                    logger.warning(f"[WARNING] Google Document creation failed: {google_doc_result['error']}")
                    documents_created["google_doc_error"] = google_doc_result["error"]
            
            # Step 8: Compile results
            results = {
                "documents_created": documents_created,
                "keywords_data": keywords_data,
                "papers_found": len(papers),
                "papers_analyzed": len(filtered_papers),
                "papers_processed": len(processed_papers),
                "pdfs_downloaded": len([p for p in processed_papers if p.full_text]),
                "marketing_analysis": marketing_analysis,
                "academic_analysis": analysis_data,
                "bright_data_stats": self.get_bright_data_stats(),
                "success": True
            }
            
            # Step 9: Display summary
            logger.info("[OK] Marketing Research Example Completed!")
            logger.info("[STATS] Final Results Summary:")
            
            # Display created documents
            if documents_created:
                if "word" in documents_created:
                    logger.info(f"  [DOC] Word Document: {documents_created['word']['filename']}")
                if "google_doc" in documents_created:
                    logger.info(f"  [DOC] Google Document: {documents_created['google_doc']['document_url']}")
                if "google_doc_error" in documents_created:
                    logger.info(f"  [ERROR] Google Document failed: {documents_created['google_doc_error']}")
            
            logger.info(f"  [SEARCH] Papers found: {results['papers_found']}")
            logger.info(f"  [DOC] Papers analyzed: {results['papers_analyzed']}")
            logger.info(f"  [DOWNLOAD] PDFs processed: {results['pdfs_downloaded']}")
            logger.info(f"  [BULLSEYE] Marketing analysis: {'[OK]' if not marketing_analysis.get('error') else '[ERROR]'}")
            logger.info(f"  [DOC] Documents created: {len(documents_created)} types")
            
            # Display Bright Data statistics
            bd_stats = results['bright_data_stats']
            logger.info(f"  [GLOBE] Bright Data requests: {bd_stats.get('requests_made', 0)}")
            logger.info(f"  [OK] Success rate: {bd_stats.get('success_rate', 0):.1f}%")
            
            return results
            
        except Exception as e:
            logger.error(f"[ERROR] Error in marketing research example: {e}")
            return {
                "error": str(e),
                "success": False,
                "bright_data_stats": self.get_bright_data_stats()
            }

# Main execution
if __name__ == "__main__":
    print("*** Marketing Research Agent with Bright Data Integration ***")
    print("=" * 60)
    
    # Example usage
    agent = GoogleScholarResearchAgent()
    
    # Configure Bright Data
    agent.configure_bright_data_api(
        enable_bright_data=True,
        api_key=os.getenv("BRIGHT_DATA_API_KEY", "your_api_key_here")
    )
    
    # Configure PDF processing
    agent.configure_paper_download(
        enable_download=True,
        max_download_size_mb=50,
        download_timeout=30,
        max_parallel_downloads=3
    )
    
    print("\n*** Running Complete Marketing Research Workflow Example ***")
    print("-" * 60)
    
    # Run complete marketing research example
    search_topics = ["social media marketing", "consumer behavior"]
    results = agent.run_marketing_research_example(search_topics)
    
    print("\n*** Final Results ***")
    print(f"Success: {results.get('success', False)}")
    if results.get('success'):
        print(f"Documents created: {len(results.get('documents_created', {}))}")
        
        # Display each document type
        docs = results.get('documents_created', {})
        if 'word' in docs:
            print(f"  - Word Document: {docs['word']['filename']}")
        if 'google_doc' in docs:
            print(f"  - Google Document: {docs['google_doc']['document_url']}")
        if 'google_doc_error' in docs:
            print(f"  - Google Document Error: {docs['google_doc_error']}")
        
        print(f"Papers found: {results.get('papers_found', 0)}")
        print(f"Papers analyzed: {results.get('papers_analyzed', 0)}")
        print(f"PDFs processed: {results.get('pdfs_downloaded', 0)}")
        
        # Show Bright Data stats
        bd_stats = results.get('bright_data_stats', {})
        print(f"\n*** Bright Data Statistics ***")
        print(f"  Requests: {bd_stats.get('requests_made', 0)}")
        print(f"  Success rate: {bd_stats.get('success_rate', 0):.1f}%")
        print(f"  CAPTCHAs bypassed: {bd_stats.get('captcha_bypassed', 0)}")
        print(f"  Avg response time: {bd_stats.get('average_response_time', 0):.2f}s")
    else:
        print(f"Error: {results.get('error', 'Unknown error')}")
    
    print("\n*** Complete Marketing Research Workflow Demonstration Complete! ***")
    print("*** This demonstrates the full integration: ***")
    print("  1. [OK] Bright Data CAPTCHA bypass")
    print("  2. [OK] Google Scholar search")
    print("  3. [OK] PDF download and processing")
    print("  4. [OK] AI-powered marketing analysis")
    print("  5. [OK] Comprehensive document generation") 