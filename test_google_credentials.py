#!/usr/bin/env python3
"""
Google Credentials Test Script
This script helps verify that your Google API credentials are set up correctly.
"""

import os
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google API scopes needed for the research agent
SCOPES = [
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.file'
]

def check_credentials_file():
    """Check if credentials.json exists and is valid"""
    print("🔍 Checking credentials.json file...")
    
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json file not found!")
        print("📋 Please follow the setup guide to create this file.")
        return False
    
    try:
        with open('credentials.json', 'r') as f:
            credentials_data = json.load(f)
        
        # Check if it has the required structure
        if 'installed' not in credentials_data:
            print("❌ Invalid credentials.json structure!")
            print("📋 The file should contain an 'installed' section.")
            return False
        
        installed = credentials_data['installed']
        required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
        
        for field in required_fields:
            if field not in installed:
                print(f"❌ Missing required field: {field}")
                return False
        
        print("✅ credentials.json file looks valid!")
        print(f"📋 Client ID: {installed['client_id'][:20]}...")
        print(f"📋 Project ID: {installed.get('project_id', 'Not specified')}")
        return True
        
    except json.JSONDecodeError:
        print("❌ credentials.json is not valid JSON!")
        return False
    except Exception as e:
        print(f"❌ Error reading credentials.json: {e}")
        return False

def authenticate_google_services():
    """Authenticate with Google services"""
    print("\n🔐 Authenticating with Google services...")
    
    creds = None
    
    # Check if token.json exists
    if os.path.exists('token.json'):
        print("📋 Found existing token.json file")
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            print(f"⚠️  Error loading token.json: {e}")
            print("🔄 Will create new token...")
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired credentials...")
            try:
                creds.refresh(Request())
                print("✅ Credentials refreshed successfully!")
            except Exception as e:
                print(f"❌ Error refreshing credentials: {e}")
                print("🔄 Will create new credentials...")
                creds = None
        
        if not creds:
            print("🌐 Starting OAuth flow...")
            print("📋 A browser window will open for authentication")
            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
                print("✅ OAuth flow completed successfully!")
            except Exception as e:
                print(f"❌ Error during OAuth flow: {e}")
                return None
        
        # Save the credentials for the next run
        try:
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            print("✅ token.json saved successfully!")
        except Exception as e:
            print(f"⚠️  Warning: Could not save token.json: {e}")
    
    return creds

def test_google_docs_api(creds):
    """Test Google Docs API access"""
    print("\n📄 Testing Google Docs API...")
    
    try:
        service = build('docs', 'v1', credentials=creds)
        print("✅ Google Docs API service created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating Google Docs service: {e}")
        return False

def test_google_drive_api(creds):
    """Test Google Drive API access"""
    print("\n📁 Testing Google Drive API...")
    
    try:
        service = build('drive', 'v3', credentials=creds)
        print("✅ Google Drive API service created successfully!")
        
        # Try to list some files (limit to 5 for testing)
        results = service.files().list(
            pageSize=5, fields="nextPageToken, files(id, name)").execute()
        files = results.get('files', [])
        
        if files:
            print(f"📋 Successfully accessed your Drive files! Found {len(files)} files:")
            for file in files:
                print(f"  - {file['name']} (ID: {file['id']})")
        else:
            print("📋 No files found in your Drive (or access limited)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error accessing Google Drive: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Google Credentials Test Script")
    print("=" * 40)
    
    # Step 1: Check credentials.json
    if not check_credentials_file():
        print("\n❌ Credentials setup incomplete!")
        print("📋 Please follow the GOOGLE_CREDENTIALS_SETUP.md guide")
        return
    
    # Step 2: Authenticate
    creds = authenticate_google_services()
    if not creds:
        print("\n❌ Authentication failed!")
        return
    
    # Step 3: Test APIs
    docs_ok = test_google_docs_api(creds)
    drive_ok = test_google_drive_api(creds)
    
    # Final results
    print("\n🎯 Test Results Summary:")
    print("=" * 40)
    print(f"📄 Google Docs API: {'✅ Working' if docs_ok else '❌ Failed'}")
    print(f"📁 Google Drive API: {'✅ Working' if drive_ok else '❌ Failed'}")
    
    if docs_ok and drive_ok:
        print("\n🎉 All tests passed! Your Google credentials are set up correctly.")
        print("📋 You can now use the research agent with Google services.")
    else:
        print("\n⚠️  Some tests failed. Please check your setup.")
        print("📋 Refer to the GOOGLE_CREDENTIALS_SETUP.md guide for troubleshooting.")

if __name__ == "__main__":
    main() 