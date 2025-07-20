"""
Trello Members Debug Tool - Test member assignment functionality
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Get credentials from environment
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')

print("👥 TRELLO MEMBERS DEBUG TOOL")
print("=" * 50)

if not all([TRELLO_API_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID]):
    print("❌ Missing credentials! Please check your .env file.")
    exit(1)

# Test board members access
print("\n1️⃣ TESTING BOARD MEMBERS ACCESS:")
members_url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/members"
members_params = {
    'key': TRELLO_API_KEY,
    'token': TRELLO_TOKEN
}

try:
    response = requests.get(members_url, params=members_params)
    if response.status_code == 200:
        members_data = response.json()
        print(f"   ✅ Found {len(members_data)} board members:")
        
        for i, member in enumerate(members_data, 1):
            username = member.get('username', 'No username')
            fullname = member.get('fullName', 'No full name')
            initials = member.get('initials', 'No initials')
            member_id = member.get('id', 'No ID')
            
            print(f"      {i}. {fullname} (@{username})")
            print(f"         Initials: {initials}")
            print(f"         ID: {member_id}")
            print()
        
        # Test member assignment mapping
        print("\n2️⃣ TESTING MEMBER NAME MAPPING:")
        team_members = ['Sebastian', 'Scott', 'Rana', 'Ilia']
        
        # Name mappings from the code
        name_mappings = {
            'sebastian': ['sebastian', 'sebas'],
            'scott': ['scott'],
            'rana': ['rana'],
            'ilia': ['ilia']
        }
        
        def find_member_by_name(assignee_name: str, board_members: list):
            assignee_lower = assignee_name.lower()
            possible_names = name_mappings.get(assignee_lower, [assignee_lower])
            
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
        
        for team_member in team_members:
            found_member = find_member_by_name(team_member, members_data)
            if found_member:
                print(f"   ✅ {team_member} → {found_member['fullName']} (@{found_member['username']})")
            else:
                print(f"   ❌ {team_member} → No match found")
        
        if len(members_data) == 0:
            print("\n💡 No board members found. This could mean:")
            print("   - The board has no members added")
            print("   - You need to invite team members to the board")
            print("   - Members need to accept board invitations")
            
    else:
        print(f"   ❌ Members access failed: {response.status_code}")
        print(f"   Error: {response.text}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n✅ MEMBER TESTING COMPLETED!")
print("\n💡 To assign tasks to specific people:")
print("   1. Make sure team members are added to your Trello board")
print("   2. Their Trello usernames/names should match or contain:")
print("      - Sebastian: 'sebastian' or 'sebas'")
print("      - Scott: 'scott'")
print("      - Rana: 'rana'") 
print("      - Ilia: 'ilia'")
print("   3. Cards will be automatically assigned to matching members") 