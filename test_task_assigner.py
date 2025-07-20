#!/usr/bin/env python3
"""
Quick test script to verify TaskAssigner setup and functionality
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_task_assigner():
    """Test TaskAssigner import and basic setup"""
    print("🔧 Testing TaskAssigner setup...")
    
    try:
        # Try to import TaskAssigner
        print("📦 Importing TaskAssigner...")
        sys.path.append('task assigner')
        from task_assigner import TaskAssigner
        print("✅ TaskAssigner imported successfully")
        
        # Check for required files
        print("\n🔍 Checking required files...")
        
        required_files = [
            'service-account.json',
            'task assigner/service-account.json',
            '.env'
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                print(f"✅ Found: {file_path}")
            else:
                print(f"⚠️ Missing: {file_path}")
        
        # Check environment variables
        print("\n🌐 Checking environment variables...")
        
        env_vars = [
            'OPENAI_API_KEY',
            'TRELLO_API_KEY', 
            'TRELLO_TOKEN',
            'TRELLO_BOARD_ID'
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                print(f"✅ {var}: {'*' * min(len(value), 10)}...")
            else:
                print(f"⚠️ {var}: Not set")
        
        # Try to initialize TaskAssigner
        print("\n🚀 Initializing TaskAssigner...")
        try:
            task_assigner = TaskAssigner()
            print("✅ TaskAssigner initialized successfully")
            
            # Test team members
            if hasattr(task_assigner, 'team_members'):
                print(f"👥 Team members loaded: {len(task_assigner.team_members)}")
                for member in task_assigner.team_members:
                    print(f"   - {member.name}: {len(member.keywords)} keywords")
            else:
                print("⚠️ No team members found")
                
        except Exception as e:
            print(f"❌ Failed to initialize TaskAssigner: {e}")
            return False
        
        print("\n🎉 TaskAssigner test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import TaskAssigner: {e}")
        print("💡 Make sure task_assigner.py is in the 'task assigner' directory")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 TaskAssigner Test Script")
    print("=" * 50)
    
    success = test_task_assigner()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed! TaskAssigner is ready to use.")
    else:
        print("❌ Some tests failed. Please check the setup.")
        
    print("\n💡 Tips:")
    print("   - Make sure service-account.json is in the right location")
    print("   - Set up environment variables in .env file")
    print("   - Check Trello API credentials")
    print("   - Verify OpenAI API key is valid") 