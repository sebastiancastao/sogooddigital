#!/usr/bin/env python3
"""
Quick setup and test script for Bright Data API
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("BRIGHT_DATA_API_KEY")

if not api_key:
    print("❌ Error: BRIGHT_DATA_API_KEY environment variable not set")
    print("Please set it with: export BRIGHT_DATA_API_KEY='your_api_key_here'")
    exit(1)

def setup_environment():
    """Set up environment variables for Bright Data API"""
    print("🔧 Setting up Bright Data API environment...")
    
    # Your API key
    # api_key = "26ca0b85-c197-4f30-8b44-acb65771f482" # This line is removed
    
    # Set environment variable for this session
    os.environ["BRIGHT_DATA_API_KEY"] = api_key
    
    print(f"✅ BRIGHT_DATA_API_KEY set: {api_key[:8]}...{api_key[-4:]}")
    
    # Check if OpenAI key exists
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("⚠️ OPENAI_API_KEY not found - you may need to set this for full functionality")
        print("  You can set it with: export OPENAI_API_KEY='your_openai_key'")
    else:
        print(f"✅ OPENAI_API_KEY found: {openai_key[:8]}...{openai_key[-4:]}")

def quick_test():
    """Run a quick test of the Bright Data API"""
    print("\n🧪 Running quick test...")
    
    try:
        import requests
        
        # api_key = os.getenv("BRIGHT_DATA_API_KEY") # This line is removed
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Simple test request
        data = {
            "zone": "web_unlocker1",
            "url": "https://httpbin.org/ip",
            "format": "raw"
        }
        
        print("📤 Making test request to Bright Data API...")
        
        response = requests.post(
            "https://api.brightdata.com/request",
            json=data,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ API test successful!")
            print(f"Response: {response.text[:100]}...")
            return True
        else:
            print(f"❌ API test failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_google_scholar():
    """Test Google Scholar access via Bright Data"""
    print("\n🎓 Testing Google Scholar access...")
    
    try:
        from google_scholar_research_agent import GoogleScholarResearchAgent
        
        # Initialize agent
        agent = GoogleScholarResearchAgent()
        
        # Configure Bright Data
        agent.configure_bright_data_api(
            enable_bright_data=True,
            zone="web_unlocker1",
            request_timeout=60,
            max_retries=3
        )
        
        # Test direct search
        print("🔍 Testing search: 'artificial intelligence'")
        papers = agent._search_scholar_with_bright_data("artificial intelligence")
        
        if papers:
            print(f"✅ Found {len(papers)} papers!")
            for i, paper in enumerate(papers[:3], 1):
                title = paper.get('title', 'No title')
                print(f"  {i}. {title[:60]}...")
            return True
        else:
            print("❌ No papers found")
            return False
            
    except Exception as e:
        print(f"❌ Google Scholar test failed: {e}")
        return False

def show_usage_example():
    """Show usage example"""
    print("\n" + "="*60)
    print("📖 USAGE EXAMPLE")
    print("="*60)
    
    example_code = '''
from google_scholar_research_agent import GoogleScholarResearchAgent

# Initialize the agent
agent = GoogleScholarResearchAgent()

# The API key is already set in environment, so just configure
agent.configure_bright_data_api(
    enable_bright_data=True,
    zone="web_unlocker1",
    request_timeout=60,
    max_retries=3
)

# Search for papers (Bright Data will handle CAPTCHAs automatically)
papers = agent.search_google_scholar([
    "machine learning algorithms",
    "deep learning optimization"
])

print(f"Found {len(papers)} papers!")
for paper in papers[:5]:
    print(f"- {paper.title}")

# Get Bright Data statistics
stats = agent.get_bright_data_stats()
print(f"Success rate: {stats['success_rate']:.1f}%")
'''
    
    print(example_code)

def main():
    """Main setup function"""
    print("🌐 BRIGHT DATA API SETUP")
    print("="*40)
    
    # Setup environment
    setup_environment()
    
    # Quick API test
    if quick_test():
        print("\n🎉 Basic API connectivity works!")
        
        # Test Google Scholar
        if test_google_scholar():
            print("\n🎉 Google Scholar integration works!")
            
            # Show usage example
            show_usage_example()
            
            print("\n✅ Setup complete! You can now use Bright Data for CAPTCHA bypass.")
            print("Run 'python test_bright_data_debug.py' for comprehensive testing.")
            
        else:
            print("\n⚠️ Google Scholar integration needs troubleshooting.")
            print("Run 'python test_bright_data_debug.py' for detailed debugging.")
    else:
        print("\n❌ Basic API connectivity failed.")
        print("Please check:")
        print("- Your API key is valid")
        print("- You have internet connectivity")
        print("- Bright Data service is available")

if __name__ == "__main__":
    main() 