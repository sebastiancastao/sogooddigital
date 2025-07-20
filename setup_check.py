"""
Setup checker for Task Assigner
Verifies all required configuration is present and valid
"""

import os
import sys
from config import Config, EXAMPLE_ENV_VARS

def check_environment_variables():
    """Check if all required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    try:
        Config.validate()
        print("✅ All required environment variables are set")
        return True
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n📝 Please create a .env file with the following variables:")
        print(EXAMPLE_ENV_VARS)
        return False

def check_google_credentials():
    """Check if Google credentials file exists"""
    print("🔍 Checking Google credentials...")
    
    if os.path.exists(Config.GOOGLE_CREDENTIALS_FILE):
        print(f"✅ Google credentials file found: {Config.GOOGLE_CREDENTIALS_FILE}")
        return True
    else:
        print(f"❌ Google credentials file not found: {Config.GOOGLE_CREDENTIALS_FILE}")
        print("   Please download your credentials.json from Google Cloud Console")
        print("   and place it in the project root directory")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'openai',
        'google-api-python-client',
        'google-auth-oauthlib',
        'requests',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("   Please install with: pip install -r requirements.txt")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def test_api_connections():
    """Test API connections"""
    print("🔍 Testing API connections...")
    
    # Test OpenAI
    try:
        import openai
        openai.api_key = Config.OPENAI_API_KEY
        # Simple test without making actual API call
        print("✅ OpenAI API key configured")
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        return False
    
    # Test Trello
    try:
        import requests
        url = f"https://api.trello.com/1/boards/{Config.TRELLO_BOARD_ID}"
        params = {
            'key': Config.TRELLO_API_KEY,
            'token': Config.TRELLO_TOKEN
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            board_data = response.json()
            print(f"✅ Trello board accessible: {board_data.get('name', 'Unknown')}")
        else:
            print(f"❌ Trello API error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Trello API error: {e}")
        return False
    
    return True

def main():
    """Main setup check function"""
    print("🚀 Task Assigner Setup Check")
    print("=" * 40)
    
    checks = [
        check_dependencies,
        check_environment_variables,
        check_google_credentials,
        test_api_connections
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
        print()
    
    if all_passed:
        print("🎉 All checks passed! You're ready to use the Task Assigner.")
        print("\nTo get started:")
        print("1. Find your Google Doc ID from the URL")
        print("2. Run: python task_assigner.py YOUR_DOC_ID")
        print("3. Or use the example: python example_usage.py")
    else:
        print("❌ Some checks failed. Please fix the issues above and try again.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 