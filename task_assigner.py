"""
Task Assigner - Google Docs to Trello Task Assignment
Processes Google Docs content with OpenAI, assigns tasks to team members, and creates Trello cards.
"""

import os
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
import re

# Third-party imports
import openai
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import requests
# Local imports
from config import Config
from google_credentials_helper import GoogleCredentialsHelper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TeamMember:
    """Represents a team member with their responsibilities"""
    def __init__(self, name: str, responsibilities: List[str], keywords: List[str]):
        self.name = name
        self.responsibilities = responsibilities
        self.keywords = keywords

class TaskAssigner:
    """Main class for processing Google Docs and assigning tasks"""
    
    def __init__(self):
        self.setup_apis()
        self.setup_team_members()
        
    def setup_apis(self):
        """Initialize API credentials and clients"""
        # Validate configuration
        Config.validate()
        
        # OpenAI setup
        openai.api_key = Config.OPENAI_API_KEY
        
        # Trello setup
        self.trello_api_key = Config.TRELLO_API_KEY
        self.trello_token = Config.TRELLO_TOKEN
        self.trello_board_id = Config.TRELLO_BOARD_ID
        
        # Google Docs setup
        self.google_creds = None
        self.setup_google_docs()
        
    def setup_google_docs(self):
        """Setup Google Docs API credentials using environment variables or service account files"""
        SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
        
        # Use GoogleCredentialsHelper to get credentials
        self.google_creds = GoogleCredentialsHelper.get_google_credentials(SCOPES)
        
        if not self.google_creds:
            raise ValueError("Could not setup Google Docs API credentials. Please check your environment variables or service account files.")
        
        self.docs_service = build('docs', 'v1', credentials=self.google_creds)
    
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
    
    def extract_text_from_google_doc(self, doc_id: str) -> str:
        """Extract text content from a Google Doc"""
        try:
            doc = self.docs_service.documents().get(documentId=doc_id).execute()
            content = doc.get('body', {}).get('content', [])
            
            text = ""
            for element in content:
                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    for text_run in paragraph.get('elements', []):
                        if 'textRun' in text_run:
                            text += text_run['textRun']['content']
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from Google Doc: {str(e)}")
            raise
    
    def process_content_with_openai(self, content: str) -> List[Dict]:
        """Process content with OpenAI to extract tasks"""
        try:
            prompt = f"""
            Context: You are analyzing content for a marketing agency. The team specializes in digital marketing services including social media management, content strategy, SEO, and business automation.
            
            Analyze the following marketing agency content and extract actionable tasks. For each task, provide:
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
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a task extraction expert for a marketing agency. Extract actionable marketing tasks from content and format them as JSON. Consider the marketing agency context and team specializations when categorizing tasks."},
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
        
        # Common name mappings (you can customize these)
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
    
    def create_trello_card(self, task: Dict, assignee: str) -> Dict:
        """Create a Trello card for the assigned task and assign to team member"""
        try:
            # Get board members first
            board_members = self.get_board_members()
            
            # Get list ID for the assignee (you might want to create separate lists for each team member)
            lists_url = f"https://api.trello.com/1/boards/{self.trello_board_id}/lists"
            lists_params = {
                'key': self.trello_api_key,
                'token': self.trello_token
            }
            
            lists_response = requests.get(lists_url, params=lists_params)
            lists_data = lists_response.json()
            
            # Find or create a list for the assignee
            assignee_list = None
            for list_item in lists_data:
                if assignee.lower() in list_item['name'].lower():
                    assignee_list = list_item
                    break
            
            if not assignee_list:
                # Use the first list if no specific assignee list found
                assignee_list = lists_data[0] if lists_data else None
            
            if not assignee_list:
                raise ValueError("No suitable list found on Trello board")
            
            # Prepare card data
            card_data = {
                'key': self.trello_api_key,
                'token': self.trello_token,
                'idList': assignee_list['id'],
                'name': task['title'],
                'desc': self.format_task_description(task, assignee),
                'pos': 'top'
            }
            
            # Add due date if specified
            if task.get('deadline'):
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
                else:
                    logger.info(f"No board members found - card created without assignment")
                
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
    
    def process_google_doc(self, doc_id: str) -> Dict:
        """Main method to process a Google Doc and create assigned tasks"""
        try:
            logger.info(f"Processing Google Doc: {doc_id}")
            
            # Extract text from Google Doc
            content = self.extract_text_from_google_doc(doc_id)
            logger.info(f"Extracted {len(content)} characters from document")
            
            # Process with OpenAI to extract tasks
            tasks = self.process_content_with_openai(content)
            logger.info(f"Extracted {len(tasks)} tasks from content")
            
            # Assign tasks and create Trello cards
            results = {
                'total_tasks': len(tasks),
                'tasks': tasks,  # Include the full task details
                'assignments': {},
                'trello_cards': [],
                'errors': []
            }
            
            for task in tasks:
                try:
                    # Assign to team member
                    assignee = self.assign_task_to_team_member(task)
                    
                    # Add assignee to task data
                    task['assignee'] = assignee
                    
                    # Update assignment counts
                    if assignee not in results['assignments']:
                        results['assignments'][assignee] = 0
                    results['assignments'][assignee] += 1
                    
                    # Create Trello card
                    card_info = self.create_trello_card(task, assignee)
                    if card_info:
                        results['trello_cards'].append({
                            'task': task['title'],
                            'assignee': assignee,
                            'card_id': card_info['id'],
                            'card_url': card_info['url']
                        })
                    
                except Exception as e:
                    error_msg = f"Error processing task '{task.get('title', 'Unknown')}': {str(e)}"
                    logger.error(error_msg)
                    results['errors'].append(error_msg)
            
            logger.info(f"Processing complete. Created {len(results['trello_cards'])} Trello cards")
            return results
            
        except Exception as e:
            logger.error(f"Error in process_google_doc: {str(e)}")
            raise

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process Google Doc and assign tasks to team members')
    parser.add_argument('doc_id', help='Google Doc ID (from the URL)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        assigner = TaskAssigner()
        results = assigner.process_google_doc(args.doc_id)
        
        print("\n" + "="*50)
        print("TASK ASSIGNMENT RESULTS")
        print("="*50)
        print(f"Total tasks extracted: {results['total_tasks']}")
        print(f"Trello cards created: {len(results['trello_cards'])}")
        
        # Show detailed tasks
        print("\n" + "="*50)
        print("EXTRACTED TASKS DETAILS")
        print("="*50)
        for i, task in enumerate(results.get('tasks', []), 1):
            print(f"\n📋 Task {i}: {task.get('title', 'Untitled')}")
            print(f"   👤 Assigned to: {task.get('assignee', 'Unassigned')}")
            print(f"   📝 Description: {task.get('description', 'No description')}")
            print(f"   ⚡ Priority: {task.get('priority', 'Not specified')}")
            print(f"   💪 Effort: {task.get('effort', 'Not specified')}")
            print(f"   📂 Category: {task.get('category', 'Not specified')}")
            if task.get('deadline'):
                print(f"   📅 Deadline: {task.get('deadline')}")
            if task.get('requirements'):
                print(f"   📋 Requirements: {', '.join(task.get('requirements', []))}")
        
        print("\n" + "="*50)
        print("TASKS BY TEAM MEMBER")
        print("="*50)
        
        # Group tasks by assignee
        tasks_by_assignee = {}
        for task in results.get('tasks', []):
            assignee = task.get('assignee', 'Unassigned')
            if assignee not in tasks_by_assignee:
                tasks_by_assignee[assignee] = []
            tasks_by_assignee[assignee].append(task)
        
        # Display tasks grouped by assignee
        for assignee, tasks in tasks_by_assignee.items():
            print(f"\n👤 {assignee} ({len(tasks)} tasks):")
            for i, task in enumerate(tasks, 1):
                priority_emoji = "🔴" if task.get('priority') == 'High' else "🟡" if task.get('priority') == 'Medium' else "🟢"
                print(f"   {i}. {priority_emoji} {task.get('title', 'Untitled')}")
                print(f"      📂 {task.get('category', 'No category')}")
        
        print("\n" + "="*50)
        print("ASSIGNMENT SUMMARY")
        print("="*50)
        print("Task assignments:")
        for assignee, count in results['assignments'].items():
            print(f"  {assignee}: {count} tasks")
        
        if results['errors']:
            print(f"\nErrors encountered: {len(results['errors'])}")
            for error in results['errors']:
                print(f"  - {error}")
        
        print("\nTrello cards created:")
        for card in results['trello_cards']:
            print(f"  - {card['task']} → {card['assignee']}")
            print(f"    URL: {card['card_url']}")
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 