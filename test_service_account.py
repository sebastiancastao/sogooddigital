#!/usr/bin/env python3
"""
Test script to verify service account authentication and Google Doc functionality
"""

import os
import json

def test_service_account():
    """Test service account file and Google authentication"""
    print("🧪 Testing Service Account Authentication")
    print("=" * 50)
    
    # Check service account file
    if os.path.exists('service-account.json'):
        print("✅ service-account.json found")
        
        # Validate JSON structure
        try:
            with open('service-account.json', 'r') as f:
                data = json.load(f)
            
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
            else:
                print("✅ Service account JSON structure valid")
                print(f"   📧 Client email: {data.get('client_email')}")
                print(f"   🏷️  Project ID: {data.get('project_id')}")
                
                if data.get('private_key', '').startswith('-----BEGIN PRIVATE KEY-----'):
                    print("✅ Private key format correct")
                else:
                    print("❌ Private key format incorrect")
                    
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON format: {e}")
    else:
        print("❌ service-account.json not found")
    
    print()
    
    # Check OpenAI API key
    if os.getenv('OPENAI_API_KEY'):
        print("✅ OPENAI_API_KEY environment variable set")
    else:
        print("❌ OPENAI_API_KEY environment variable not set")
    
    print()
    
    # Try to import required modules
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        print("✅ Google API libraries available")
    except ImportError as e:
        print(f"❌ Google API libraries missing: {e}")
        print("   Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    
    try:
        import openai
        print("✅ OpenAI library available")
    except ImportError as e:
        print(f"❌ OpenAI library missing: {e}")
        print("   Run: pip install openai")
    
    print()
    print("📋 Next Steps:")
    print("1. Make sure service-account.json is properly configured")
    print("2. Set OPENAI_API_KEY environment variable")
    print("3. Share Google Docs with: sebastiancastano@phonic-goods-317118.iam.gserviceaccount.com")
    print("4. Test by running the Flask app and trying to analyze a Google Doc")

def test_google_auth():
    """Test actual Google authentication"""
    print("🔐 Testing Google Authentication")
    print("=" * 50)
    
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        scopes = [
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/drive.file'
        ]
        
        if os.path.exists('service-account.json'):
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    'service-account.json', scopes=scopes)
                
                # Try to build services
                docs_service = build('docs', 'v1', credentials=credentials)
                drive_service = build('drive', 'v3', credentials=credentials)
                
                print("✅ Google authentication successful!")
                print("✅ Google Docs API ready")
                print("✅ Google Drive API ready")
                
                return True
                
            except Exception as e:
                print(f"❌ Google authentication failed: {e}")
                return False
        else:
            print("❌ service-account.json not found")
            return False
            
    except ImportError as e:
        print(f"❌ Required libraries not available: {e}")
        return False

if __name__ == "__main__":
    test_service_account()
    print()
    test_google_auth() 