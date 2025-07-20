"""
Trello API Debug Tool - Test credentials and permissions
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Get credentials from environment
TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')

print("🔍 TRELLO API DEBUG TOOL")
print("=" * 50)

# Check if credentials exist
print("\n1️⃣ CHECKING CREDENTIALS:")
print(f"   API Key: {'✅ Found' if TRELLO_API_KEY else '❌ Missing'}")
print(f"   Token: {'✅ Found' if TRELLO_TOKEN else '❌ Missing'}")
print(f"   Board ID: {'✅ Found' if TRELLO_BOARD_ID else '❌ Missing'}")

if not all([TRELLO_API_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID]):
    print("\n❌ Missing credentials! Please check your .env file.")
    print("\nYour .env file should contain:")
    print("TRELLO_API_KEY=your_api_key")
    print("TRELLO_TOKEN=your_token")
    print("TRELLO_BOARD_ID=your_board_id")
    exit(1)

print(f"\n   API Key preview: {TRELLO_API_KEY[:8]}...")
print(f"   Token preview: {TRELLO_TOKEN[:8]}...")
print(f"   Board ID: {TRELLO_BOARD_ID}")

# Test basic API access
print("\n2️⃣ TESTING BASIC API ACCESS:")
test_url = f"https://api.trello.com/1/members/me"
test_params = {
    'key': TRELLO_API_KEY,
    'token': TRELLO_TOKEN
}

try:
    response = requests.get(test_url, params=test_params)
    if response.status_code == 200:
        user_data = response.json()
        print(f"   ✅ API access successful!")
        print(f"   📝 Username: {user_data.get('username', 'Unknown')}")
        print(f"   📧 Email: {user_data.get('email', 'Unknown')}")
    else:
        print(f"   ❌ API access failed: {response.status_code}")
        print(f"   Error: {response.text}")
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test board access
print("\n3️⃣ TESTING BOARD ACCESS:")
board_url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}"
board_params = {
    'key': TRELLO_API_KEY,
    'token': TRELLO_TOKEN
}

try:
    response = requests.get(board_url, params=board_params)
    if response.status_code == 200:
        board_data = response.json()
        print(f"   ✅ Board access successful!")
        print(f"   📋 Board name: {board_data.get('name', 'Unknown')}")
        print(f"   🔗 Board URL: {board_data.get('url', 'Unknown')}")
    else:
        print(f"   ❌ Board access failed: {response.status_code}")
        print(f"   Error: {response.text}")
        if response.status_code == 404:
            print("   💡 Board not found. Check your TRELLO_BOARD_ID.")
        elif response.status_code == 401:
            print("   💡 Unauthorized. Check if you have access to this board.")
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Test lists access
print("\n4️⃣ TESTING BOARD LISTS:")
lists_url = f"https://api.trello.com/1/boards/{TRELLO_BOARD_ID}/lists"
lists_params = {
    'key': TRELLO_API_KEY,
    'token': TRELLO_TOKEN
}

try:
    response = requests.get(lists_url, params=lists_params)
    if response.status_code == 200:
        lists_data = response.json()
        print(f"   ✅ Found {len(lists_data)} lists:")
        for i, list_item in enumerate(lists_data, 1):
            print(f"      {i}. {list_item['name']} (ID: {list_item['id']})")
        
        if lists_data:
            target_list = lists_data[0]
            print(f"\n   🎯 Will use first list: '{target_list['name']}'")
            
            # Test card creation
            print("\n5️⃣ TESTING CARD CREATION:")
            card_data = {
                'key': TRELLO_API_KEY,
                'token': TRELLO_TOKEN,
                'idList': target_list['id'],
                'name': 'TEST CARD - Please delete',
                'desc': 'This is a test card created by the debug tool. Please delete it.',
                'pos': 'top'
            }
            
            card_url = "https://api.trello.com/1/cards"
            response = requests.post(card_url, data=card_data)
            
            if response.status_code == 200:
                card_info = response.json()
                print(f"   ✅ Test card created successfully!")
                print(f"   🔗 Card URL: {card_info['url']}")
                print(f"   💡 Please delete this test card from your Trello board.")
            else:
                print(f"   ❌ Card creation failed: {response.status_code}")
                print(f"   Error: {response.text}")
                if response.status_code == 401:
                    print("   💡 This suggests a permission issue with your token.")
                    print("   💡 Try regenerating your Trello token with full permissions.")
        else:
            print("   ❌ No lists found on board!")
    else:
        print(f"   ❌ Lists access failed: {response.status_code}")
        print(f"   Error: {response.text}")
        exit(1)
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

print("\n✅ ALL TESTS COMPLETED!")
print("If card creation succeeded, your Trello integration should work.") 