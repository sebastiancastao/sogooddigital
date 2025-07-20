"""
Simple Task Extractor - Shows task details without Trello integration
"""

import openai
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import json
import re
import requests
from config import Config

def extract_text_from_google_doc(doc_id: str):
    """Extract text content from a Google Doc"""
    # Setup Google Docs API
    SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
    creds = Credentials.from_service_account_file('service-account.json', scopes=SCOPES)
    docs_service = build('docs', 'v1', credentials=creds)
    
    doc = docs_service.documents().get(documentId=doc_id).execute()
    content = doc.get('body', {}).get('content', [])
    
    text = ""
    for element in content:
        if 'paragraph' in element:
            paragraph = element['paragraph']
            for text_run in paragraph.get('elements', []):
                if 'textRun' in text_run:
                    text += text_run['textRun']['content']
    
    return text.strip()

def create_trello_card(task: dict) -> dict:
    """Create a Trello card for a task"""
    try:
        # Get the first list on the board (we'll put all tasks there)
        lists_url = f"https://api.trello.com/1/boards/{Config.TRELLO_BOARD_ID}/lists"
        lists_params = {
            'key': Config.TRELLO_API_KEY,
            'token': Config.TRELLO_TOKEN
        }
        
        lists_response = requests.get(lists_url, params=lists_params)
        
        if lists_response.status_code != 200:
            print(f"❌ Trello API Error: {lists_response.status_code}")
            return None
            
        lists_data = lists_response.json()
        
        if not lists_data:
            print("❌ No lists found on Trello board")
            return None
            
        # Use the first list
        target_list = lists_data[0]
        
        # Prepare card data
        card_description = f"""
**Description:** {task.get('description', 'No description')}

**Priority:** {task.get('priority', 'Not specified')}
**Category:** {task.get('category', 'Not specified')}

**Created by:** Task Assigner AI
        """.strip()
        
        card_data = {
            'key': Config.TRELLO_API_KEY,
            'token': Config.TRELLO_TOKEN,
            'idList': target_list['id'],
            'name': task.get('title', 'Untitled Task'),
            'desc': card_description,
            'pos': 'top'
        }
        
        # Create the card
        card_url = "https://api.trello.com/1/cards"
        response = requests.post(card_url, data=card_data)
        
        if response.status_code == 200:
            card_info = response.json()
            print(f"✅ Created Trello card: {task.get('title', 'Untitled')}")
            return {
                'task': task.get('title'),
                'card_id': card_info['id'],
                'card_url': card_info['url']
            }
        else:
            print(f"❌ Failed to create Trello card: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating Trello card: {e}")
        return None

def extract_tasks_simple(content: str):
    """Extract tasks using OpenAI with simplified approach"""
    openai.api_key = Config.OPENAI_API_KEY
    
    # Simplified prompt
    prompt = f"""
    Analyze this content and extract 5-10 actionable tasks. For each task, provide:
    - Task title (brief, clear)
    - Description (1-2 sentences)
    - Priority (High/Medium/Low)
    - Category (type of work)
    
    Content: {content[:5000]}...
    
    Format as simple JSON array:
    [
      {{
        "title": "Task name",
        "description": "What needs to be done",
        "priority": "High",
        "category": "Marketing"
      }}
    ]
    """
    
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Extract actionable tasks as JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        task_text = response.choices[0].message.content.strip()
        print("Raw OpenAI Response:")
        print("=" * 50)
        print(task_text)
        print("=" * 50)
        
        # Try to extract JSON
        json_match = re.search(r'\[.*\]', task_text, re.DOTALL)
        if json_match:
            tasks = json.loads(json_match.group(0))
            return tasks
        else:
            print("No JSON array found in response")
            return []
            
    except Exception as e:
        print(f"Error with OpenAI: {e}")
        return []

def main():
    doc_id = "1boEvsPfuDylxLNY_TdPTERF3YVo3DONwJmNliyctGgs"
    
    print("📄 Extracting content from Google Doc...")
    content = extract_text_from_google_doc(doc_id)
    print(f"✅ Extracted {len(content)} characters")
    
    print("\n🤖 Processing with OpenAI...")
    tasks = extract_tasks_simple(content)
    
    if tasks:
        print(f"\n🎯 Extracted {len(tasks)} tasks:")
        print("=" * 60)
        
        for i, task in enumerate(tasks, 1):
            print(f"\n📋 Task {i}: {task.get('title', 'Untitled')}")
            print(f"   📝 Description: {task.get('description', 'No description')}")
            print(f"   ⚡ Priority: {task.get('priority', 'Not specified')}")
            print(f"   📂 Category: {task.get('category', 'Not specified')}")
        
        # Create Trello cards
        print(f"\n📋 Creating Trello cards...")
        print("=" * 60)
        
        created_cards = []
        for task in tasks:
            card_info = create_trello_card(task)
            if card_info:
                created_cards.append(card_info)
        
        # Show results
        print(f"\n🎉 RESULTS:")
        print("=" * 60)
        print(f"📊 Total tasks extracted: {len(tasks)}")
        print(f"✅ Trello cards created: {len(created_cards)}")
        
        if created_cards:
            print(f"\n🔗 Created Trello Cards:")
            for card in created_cards:
                print(f"   • {card['task']}")
                print(f"     🔗 {card['card_url']}")
        
        if len(created_cards) < len(tasks):
            failed_count = len(tasks) - len(created_cards)
            print(f"\n⚠️  {failed_count} cards failed to create (likely due to Trello API authentication)")
            
    else:
        print("❌ No tasks extracted")

if __name__ == "__main__":
    main() 