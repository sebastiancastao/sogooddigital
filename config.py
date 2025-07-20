"""
Configuration file for Task Assigner
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    """Configuration class for Task Assigner"""
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Trello Configuration
    TRELLO_API_KEY = os.getenv('TRELLO_API_KEY')
    TRELLO_TOKEN = os.getenv('TRELLO_TOKEN')
    TRELLO_BOARD_ID = os.getenv('TRELLO_BOARD_ID')
    
    # Google API Configuration
    GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    GOOGLE_TOKEN_FILE = os.getenv('GOOGLE_TOKEN_FILE', 'token.pickle')
    
    # Logging Configuration
    VERBOSE = os.getenv('VERBOSE', 'False').lower() == 'true'
    
    @classmethod
    def validate(cls):
        """Validate that all required configuration is present"""
        required_vars = [
            'OPENAI_API_KEY',
            'TRELLO_API_KEY',
            'TRELLO_TOKEN',
            'TRELLO_BOARD_ID'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

# Example environment variables for reference
EXAMPLE_ENV_VARS = """
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Trello API Configuration
TRELLO_API_KEY=your_trello_api_key_here
TRELLO_TOKEN=your_trello_token_here
TRELLO_BOARD_ID=your_trello_board_id_here

# Optional: Set to True for verbose logging
VERBOSE=False
""" 