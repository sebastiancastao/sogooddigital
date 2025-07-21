#!/usr/bin/env python3
"""
Test Script for Environment Variable Google Credentials
This script verifies that your Google service account credentials are working
using environment variables instead of JSON files.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test that all required Google environment variables are set"""
    print("🧪 Testing Google Environment Variables")
    print("=" * 50)
    
    required_vars = [
        'GOOGLE_TYPE',
        'GOOGLE_PROJECT_ID',
        'GOOGLE_PRIVATE_KEY_ID',
        'GOOGLE_PRIVATE_KEY',
        'GOOGLE_CLIENT_EMAIL',
        'GOOGLE_CLIENT_ID'
    ]
    
    optional_vars = [
        'GOOGLE_AUTH_URI',
        'GOOGLE_TOKEN_URI',
        'GOOGLE_AUTH_PROVIDER_X509_CERT_URL',
        'GOOGLE_CLIENT_X509_CERT_URL',
        'GOOGLE_UNIVERSE_DOMAIN'
    ]
    
    # Check required variables
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 20)}...")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    print()
    
    # Check optional variables
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"⚠️  {var}: Using default value")
    
    print()
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All required environment variables are set!")
        return True

def test_google_credentials():
    """Test Google credentials creation and authentication"""
    print("\n🔐 Testing Google Credentials Authentication")
    print("=" * 50)
    
    try:
        from config import Config
        from google_credentials_helper import GoogleCredentialsHelper
        
        # Test if credentials can be created from environment
        if Config.has_google_env_credentials():
            print("✅ Environment variables are properly configured")
            
            # Test credentials creation
            credentials = GoogleCredentialsHelper.create_credentials_from_env()
            if credentials:
                print("✅ Successfully created Google credentials from environment variables")
                print(f"   📧 Service account email: {credentials.service_account_email}")
                print(f"   🏷️  Project ID: {credentials.project_id}")
                
                # Test Google services
                print("\n🌐 Testing Google API Services...")
                docs_service, drive_service = GoogleCredentialsHelper.build_google_services()
                
                if docs_service and drive_service:
                    print("✅ Google Docs API service ready")
                    print("✅ Google Drive API service ready")
                    print("✅ All tests passed! Your environment variables are working correctly.")
                    return True
                else:
                    print("❌ Failed to build Google API services")
                    return False
            else:
                print("❌ Failed to create credentials from environment variables")
                return False
        else:
            print("❌ Environment variables are not properly configured")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all required dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def test_fallback_methods():
    """Test fallback authentication methods"""
    print("\n🔄 Testing Fallback Authentication Methods")
    print("=" * 50)
    
    try:
        from google_credentials_helper import GoogleCredentialsHelper
        
        # Test the complete authentication flow
        credentials = GoogleCredentialsHelper.get_google_credentials()
        
        if credentials:
            print("✅ Authentication successful using best available method")
            return True
        else:
            print("❌ All authentication methods failed")
            print("   Please check your environment variables or service account files")
            return False
            
    except Exception as e:
        print(f"❌ Fallback test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Google Environment Variables Test Suite")
    print("=" * 60)
    print()
    
    # Test 1: Environment variables
    env_test = test_environment_variables()
    
    # Test 2: Google credentials authentication
    auth_test = test_google_credentials()
    
    # Test 3: Fallback methods
    fallback_test = test_fallback_methods()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Environment Variables: {'✅ PASS' if env_test else '❌ FAIL'}")
    print(f"Google Authentication: {'✅ PASS' if auth_test else '❌ FAIL'}")
    print(f"Fallback Methods:      {'✅ PASS' if fallback_test else '❌ FAIL'}")
    print()
    
    if all([env_test, auth_test, fallback_test]):
        print("🎉 ALL TESTS PASSED!")
        print("Your Google environment variable setup is working correctly.")
        print()
        print("Next steps:")
        print("1. You can now remove the service-account.json file if desired")
        print("2. Your app will use environment variables for Google authentication")
        print("3. Environment variables take precedence over JSON files")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print()
        print("Troubleshooting:")
        print("1. Make sure you have a .env file with all Google environment variables")
        print("2. Check that the GOOGLE_PRIVATE_KEY includes proper escape sequences (\\n)")
        print("3. Verify that all required variables are set correctly")
        print("4. Ensure the google_credentials_helper.py file exists")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1) 