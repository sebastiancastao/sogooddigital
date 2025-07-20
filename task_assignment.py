"""
Flask-Integrated Task Assigner - Google Docs to Trello Task Assignment

This module integrates the task assignment functionality with the Flask web application,
providing real-time progress updates and web-friendly interfaces.
"""

import os
import json
import logging
import time
import re
from typing import List, Dict, Optional, Callable
from datetime import datetime

# Third-party imports
import openai
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import requests
from google.oauth2.credentials import Credentials as OAuthCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# Local imports
from google_credentials_helper import GoogleCredentialsHelper

# Configure logging
logger = logging.getLogger(__name__)

class TeamMember:
    """Represents a team member with their responsibilities"""
    def __init__(self, name: str, responsibilities: List[str], keywords: List[str]):
        self.name = name
        self.responsibilities = responsibilities
        self.keywords = keywords

class FlaskTaskAssigner:
    """Flask-integrated Task Assigner for processing Google Docs and assigning tasks"""
    
    def __init__(self, openai_api_key: str = None, google_credentials_path: str = None):
        """Initialize the task assigner with optional credentials"""
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.google_credentials_path = google_credentials_path or 'credentials.json'
        
        # Trello configuration
        self.trello_api_key = os.getenv('TRELLO_API_KEY')
        self.trello_token = os.getenv('TRELLO_TOKEN')
        self.trello_board_id = os.getenv('TRELLO_BOARD_ID')
        
        # Progress callback for real-time updates
        self.progress_callback = None
        
        # Setup APIs
        self.setup_apis()
        self.setup_team_members()
        
    def setup_apis(self):
        """Initialize API credentials and clients"""
        # OpenAI setup
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
        
        # Google Docs setup
        self.google_creds = None
        self.setup_google_docs()
        
    def setup_google_docs(self):
        """Setup Google Docs API credentials using environment variables or service account files"""
        SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
        
        # Use GoogleCredentialsHelper to get credentials
        creds = GoogleCredentialsHelper.get_google_credentials(SCOPES)
        
        # Fallback to legacy OAuth flow if no service account credentials available
        if not creds:
            logger.warning("No service account credentials found, trying legacy OAuth flow...")
            
            # Try token file first (OAuth flow)
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, try OAuth flow
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                elif os.path.exists(self.google_credentials_path):
                    try:
                        # Fallback to OAuth flow
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.google_credentials_path, SCOPES)
                        creds = flow.run_local_server(port=0)
                        
                        # Save credentials for next run
                        with open('token.pickle', 'wb') as token:
                            pickle.dump(creds, token)
                    except Exception as e:
                        logger.error(f"Failed to setup Google credentials: {e}")
                        raise
        
        self.google_creds = creds
        if creds:
            self.docs_service = build('docs', 'v1', credentials=creds)
        else:
            raise ValueError("Could not setup Google Docs API credentials. Please check your environment variables or service account files.")
    
    def setup_team_members(self):
        """Initialize team members with their responsibilities and keywords"""
        self.team_members = [
            TeamMember(
                name="Rana",
                responsibilities=[
                    "Oversees all social media, including both organic planning and paid ad strategy",
                    "Coordinates with graphic designers and content creators as needed"
                ],
                keywords=[
                    "social media", "instagram", "facebook", "twitter", "linkedin", "tiktok",
                    "organic", "paid ads", "ad strategy", "social strategy", "content planning",
                    "graphic design", "content creation", "visual content", "social calendar",
                    "influencer", "engagement", "followers", "social posts", "campaigns"
                ]
            ),
            TeamMember(
                name="Scott",
                responsibilities=[
                    "Leads written content and content strategy",
                    "Covers blogs, case studies, and sometimes SEO from a PR and visibility perspective"
                ],
                keywords=[
                    "content strategy", "blog", "blogs", "writing", "content creation",
                    "case studies", "case study", "articles", "copywriting", "content marketing",
                    "PR", "public relations", "visibility", "thought leadership", "storytelling",
                    "editorial", "content calendar", "brand voice", "messaging", "press release",
                    "guest posts", "content audit", "content optimization"
                ]
            ),
            TeamMember(
                name="Sebastian",
                responsibilities=[
                    "Supports day-to-day SEO tasks, metadata updates",
                    "Assists with task management or research where needed"
                ],
                keywords=[
                    "SEO", "metadata", "meta description", "title tags", "keywords",
                    "search engine", "google", "rankings", "optimization", "technical SEO",
                    "task management", "research", "data analysis", "reporting", "analytics",
                    "google analytics", "search console", "backlinks", "site audit",
                    "schema markup", "page speed", "crawling", "indexing", "SERP"
                ]
            ),
            TeamMember(
                name="Ilia",
                responsibilities=[
                    "Provides strategic oversight and supports where cross-team input is needed"
                ],
                keywords=[
                    "strategy", "strategic", "oversight", "cross-team", "collaboration",
                    "planning", "roadmap", "vision", "goals", "objectives", "leadership",
                    "coordination", "alignment", "decision making", "project management",
                    "stakeholder", "budget", "resources", "performance", "metrics", "KPIs"
                ]
            )
        ]
    
    def set_progress_callback(self, callback: Callable[[str, int], None]):
        """Set a callback function for progress updates"""
        self.progress_callback = callback
    
    def update_progress(self, message: str, progress: int):
        """Update progress and call callback if set"""
        if self.progress_callback:
            self.progress_callback(message, progress)
        logger.info(f"Progress {progress}%: {message}")
    
    def validate_configuration(self) -> Dict[str, bool]:
        """Validate that all required APIs are configured"""
        validation = {
            'openai': bool(self.openai_api_key),
            'google_docs': bool(self.google_creds),
            'trello': bool(self.trello_api_key and self.trello_token and self.trello_board_id)
        }
        return validation
    
    def extract_text_from_google_doc(self, doc_id: str) -> str:
        """Extract text content from a Google Doc"""
        try:
            self.update_progress("Connecting to Google Docs...", 5)
            
            doc = self.docs_service.documents().get(documentId=doc_id).execute()
            content = doc.get('body', {}).get('content', [])
            
            self.update_progress("Extracting text content...", 10)
            
            text = ""
            for element in content:
                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    for text_run in paragraph.get('elements', []):
                        if 'textRun' in text_run:
                            text += text_run['textRun']['content']
            
            self.update_progress(f"Extracted {len(text)} characters from document", 15)
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from Google Doc: {str(e)}")
            raise
    
    def process_content_with_openai(self, content: str) -> List[Dict]:
        """Process content with OpenAI to extract tasks"""
        try:
            self.update_progress("Analyzing content with AI to extract tasks...", 25)
            
            prompt = f"""
            Analyze the following content and extract actionable tasks. For each task, provide:
            1. A clear, specific task description
            2. Priority level (High, Medium, Low)
            3. Estimated effort (Small, Medium, Large)
            4. Suggested deadline (if mentioned or can be inferred)
            5. Task category/type
            6. Any dependencies or prerequisites
            7. Key requirements or deliverables
            
            Content to analyze:
            {content}
            
            Return the response as a JSON array of tasks, where each task has the following structure:
            {{
                "title": "Task title",
                "description": "Detailed description",
                "priority": "High/Medium/Low",
                "effort": "Small/Medium/Large",
                "deadline": "YYYY-MM-DD or null",
                "category": "Task category",
                "dependencies": ["list of dependencies"],
                "requirements": ["list of requirements"],
                "keywords": ["relevant keywords for assignment"]
            }}
            """
            
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a task extraction expert. Extract actionable tasks from content and format them as JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # Parse the JSON response
            task_text = response.choices[0].message.content.strip()
            
            # Extract JSON from the response (in case it's wrapped in markdown)
            json_match = re.search(r'```json\n(.*)\n```', task_text, re.DOTALL)
            if json_match:
                task_text = json_match.group(1)
            elif task_text.startswith('```') and task_text.endswith('```'):
                task_text = task_text[3:-3].strip()
            
            tasks = json.loads(task_text)
            self.update_progress(f"Extracted {len(tasks)} tasks from content", 40)
            return tasks
            
        except Exception as e:
            logger.error(f"Error processing content with OpenAI: {str(e)}")
            raise
    
    def assign_task_to_team_member(self, task: Dict) -> str:
        """Assign a task to the most appropriate team member"""
        try:
            # Combine task title, description, and keywords for analysis
            task_content = f"{task.get('title', '')} {task.get('description', '')} {' '.join(task.get('keywords', []))}"
            task_content = task_content.lower()
            
            # Score each team member based on keyword matches
            scores = {}
            for member in self.team_members:
                score = 0
                for keyword in member.keywords:
                    if keyword.lower() in task_content:
                        score += 1
                
                # Bonus for exact matches in title
                title_lower = task.get('title', '').lower()
                for keyword in member.keywords:
                    if keyword.lower() in title_lower:
                        score += 2
                
                scores[member.name] = score
            
            # Find the member with the highest score
            best_member = max(scores, key=scores.get)
            
            # If no clear match, use category-based assignment
            if scores[best_member] == 0:
                category = task.get('category', '').lower()
                if any(word in category for word in ['social', 'media', 'campaign', 'ad']):
                    return "Rana"
                elif any(word in category for word in ['content', 'blog', 'writing', 'pr']):
                    return "Scott"
                elif any(word in category for word in ['seo', 'technical', 'analytics', 'research']):
                    return "Sebastian"
                else:
                    return "Ilia"  # Default to strategic oversight
            
            return best_member
            
        except Exception as e:
            logger.error(f"Error assigning task to team member: {str(e)}")
            return "Ilia"  # Default assignment
    
    def get_board_members(self):
        """Get all members of the Trello board"""
        try:
            members_url = f"https://api.trello.com/1/boards/{self.trello_board_id}/members"
            members_params = {
                'key': self.trello_api_key,
                'token': self.trello_token
            }
            
            response = requests.get(members_url, params=members_params)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Could not get board members: {response.status_code}")
                return []
        except Exception as e:
            logger.warning(f"Error getting board members: {e}")
            return []
    
    def find_member_by_name(self, assignee_name: str, board_members: list):
        """Find a Trello member by name or similar"""
        assignee_lower = assignee_name.lower()
        
        # Common name mappings
        name_mappings = {
            'sebastian': ['sebastian', 'sebas'],
            'scott': ['scott'],
            'rana': ['rana'],
            'ilia': ['ilia']
        }
        
        # Get possible names for this assignee
        possible_names = name_mappings.get(assignee_lower, [assignee_lower])
        
        # Try to find member by username, full name, or initials
        for member in board_members:
            username = member.get('username', '').lower()
            fullname = member.get('fullName', '').lower()
            initials = member.get('initials', '').lower()
            
            for name in possible_names:
                if (name in username or 
                    name in fullname or 
                    name == initials or
                    username.startswith(name) or
                    fullname.startswith(name)):
                    return member
        
        return None
    
    def assign_member_to_card(self, card_id: str, member_id: str, assignee_name: str):
        """Assign a Trello member to a card"""
        try:
            assign_url = f"https://api.trello.com/1/cards/{card_id}/idMembers"
            assign_params = {
                'key': self.trello_api_key,
                'token': self.trello_token,
                'value': member_id
            }
            
            response = requests.post(assign_url, data=assign_params)
            if response.status_code == 200:
                logger.info(f"Successfully assigned {assignee_name} to Trello card")
                return True
            else:
                logger.warning(f"Failed to assign {assignee_name} to card: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.warning(f"Error assigning {assignee_name} to card: {e}")
            return False
    
    def get_or_create_list_for_assignee(self, assignee: str) -> Optional[str]:
        """Get or create a Trello list for the assignee"""
        try:
            # Get existing lists
            lists_url = f"https://api.trello.com/1/boards/{self.trello_board_id}/lists"
            lists_params = {
                'key': self.trello_api_key,
                'token': self.trello_token
            }
            
            lists_response = requests.get(lists_url, params=lists_params)
            if lists_response.status_code != 200:
                logger.error(f"Failed to get board lists: {lists_response.status_code}")
                return None
                
            lists_data = lists_response.json()
            
            # Find existing list for assignee
            for list_item in lists_data:
                if assignee.lower() in list_item['name'].lower():
                    return list_item['id']
            
            # If no specific list found, try to find a general "To Do" or similar list
            general_lists = ['to do', 'todo', 'backlog', 'tasks']
            for list_item in lists_data:
                list_name_lower = list_item['name'].lower()
                if any(general in list_name_lower for general in general_lists):
                    return list_item['id']
            
            # Return first list as fallback
            if lists_data:
                return lists_data[0]['id']
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting list for assignee {assignee}: {e}")
            return None
    
    def create_trello_card(self, task: Dict, assignee: str) -> Dict:
        """Create a Trello card for the assigned task"""
        try:
            # Get board members for assignment
            board_members = self.get_board_members()
            
            # Get appropriate list
            list_id = self.get_or_create_list_for_assignee(assignee)
            if not list_id:
                raise ValueError("No suitable list found on Trello board")
            
            # Prepare card data
            card_data = {
                'key': self.trello_api_key,
                'token': self.trello_token,
                'idList': list_id,
                'name': task['title'],
                'desc': self.format_task_description(task, assignee),
                'pos': 'top'
            }
            
            # Add due date if specified
            if task.get('deadline') and task['deadline'] != 'null':
                try:
                    card_data['due'] = task['deadline']
                except:
                    pass
            
            # Create the card
            card_url = "https://api.trello.com/1/cards"
            response = requests.post(card_url, data=card_data)
            
            if response.status_code == 200:
                card_info = response.json()
                card_id = card_info['id']
                
                # Try to assign the team member to the card
                if board_members:
                    member = self.find_member_by_name(assignee, board_members)
                    if member:
                        self.assign_member_to_card(card_id, member['id'], assignee)
                    else:
                        logger.info(f"Could not find Trello member for '{assignee}' - card created without assignment")
                
                logger.info(f"Created Trello card: {task['title']} assigned to {assignee}")
                return card_info
            else:
                logger.error(f"Failed to create Trello card: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating Trello card: {str(e)}")
            return None
    
    def format_task_description(self, task: Dict, assignee: str) -> str:
        """Format task description for Trello card"""
        description = f"**Assigned to:** {assignee}\n\n"
        description += f"**Description:** {task.get('description', '')}\n\n"
        description += f"**Priority:** {task.get('priority', 'Medium')}\n"
        description += f"**Effort:** {task.get('effort', 'Medium')}\n"
        description += f"**Category:** {task.get('category', '')}\n\n"
        
        if task.get('requirements'):
            description += "**Requirements:**\n"
            for req in task['requirements']:
                description += f"- {req}\n"
            description += "\n"
        
        if task.get('dependencies'):
            description += "**Dependencies:**\n"
            for dep in task['dependencies']:
                description += f"- {dep}\n"
            description += "\n"
        
        description += f"**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        return description
    
    def process_google_doc_for_tasks(self, doc_id: str) -> Dict:
        """Main method to process a Google Doc and create assigned tasks"""
        try:
            start_time = time.time()
            self.update_progress("Starting task extraction process...", 0)
            
            # Validate configuration first
            validation = self.validate_configuration()
            missing_configs = [k for k, v in validation.items() if not v]
            if missing_configs:
                raise ValueError(f"Missing configuration for: {', '.join(missing_configs)}")
            
            # Extract text from Google Doc
            self.update_progress("Accessing Google Document...", 5)
            content = self.extract_text_from_google_doc(doc_id)
            
            if not content.strip():
                raise ValueError("No content found in the Google Document")
            
            # Process with OpenAI to extract tasks
            tasks = self.process_content_with_openai(content)
            
            if not tasks:
                raise ValueError("No tasks could be extracted from the content")
            
            # Initialize results
            results = {
                'total_tasks': len(tasks),
                'tasks': tasks,
                'assignments': {},
                'trello_cards': [],
                'errors': [],
                'processing_time': 0,
                'document_length': len(content)
            }
            
            # Process each task
            self.update_progress("Assigning tasks to team members...", 50)
            
            for i, task in enumerate(tasks):
                try:
                    # Update progress for each task
                    task_progress = 50 + int((i / len(tasks)) * 40)
                    self.update_progress(f"Processing task {i+1} of {len(tasks)}: {task.get('title', 'Untitled')[:30]}...", task_progress)
                    
                    # Assign to team member
                    assignee = self.assign_task_to_team_member(task)
                    task['assignee'] = assignee
                    
                    # Update assignment counts
                    if assignee not in results['assignments']:
                        results['assignments'][assignee] = 0
                    results['assignments'][assignee] += 1
                    
                    # Create Trello card if Trello is configured
                    if validation['trello']:
                        card_info = self.create_trello_card(task, assignee)
                        if card_info:
                            results['trello_cards'].append({
                                'task': task['title'],
                                'assignee': assignee,
                                'card_id': card_info['id'],
                                'card_url': card_info['url']
                            })
                        else:
                            results['errors'].append(f"Failed to create Trello card for: {task['title']}")
                    
                except Exception as e:
                    error_msg = f"Error processing task '{task.get('title', 'Unknown')}': {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            # Final calculations
            results['processing_time'] = round(time.time() - start_time, 1)
            
            self.update_progress("Task assignment complete!", 100)
            logger.info(f"Processing complete. Created {len(results['trello_cards'])} Trello cards in {results['processing_time']}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in process_google_doc_for_tasks: {str(e)}")
            raise 