"""
Configuration file for Task Assigner
"""

import os
import json
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
    
    # Google API Configuration (Legacy file-based)
    GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
    GOOGLE_TOKEN_FILE = os.getenv('GOOGLE_TOKEN_FILE', 'token.pickle')
    GOOGLE_SERVICE_ACCOUNT_PATH = os.getenv('GOOGLE_SERVICE_ACCOUNT_PATH')
    
    # Google API Configuration (Environment Variables)
    GOOGLE_TYPE = os.getenv('GOOGLE_TYPE')
    GOOGLE_PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID')
    GOOGLE_PRIVATE_KEY_ID = os.getenv('GOOGLE_PRIVATE_KEY_ID')
    GOOGLE_PRIVATE_KEY = os.getenv('GOOGLE_PRIVATE_KEY')
    GOOGLE_CLIENT_EMAIL = os.getenv('GOOGLE_CLIENT_EMAIL')
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_AUTH_URI = os.getenv('GOOGLE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth')
    GOOGLE_TOKEN_URI = os.getenv('GOOGLE_TOKEN_URI', 'https://oauth2.googleapis.com/token')
    GOOGLE_AUTH_PROVIDER_X509_CERT_URL = os.getenv('GOOGLE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs')
    GOOGLE_CLIENT_X509_CERT_URL = os.getenv('GOOGLE_CLIENT_X509_CERT_URL')
    GOOGLE_UNIVERSE_DOMAIN = os.getenv('GOOGLE_UNIVERSE_DOMAIN', 'googleapis.com')
    
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
    
    @classmethod
    def has_google_env_credentials(cls):
        """Check if all required Google service account environment variables are present"""
        required_google_vars = [
            'GOOGLE_TYPE',
            'GOOGLE_PROJECT_ID',
            'GOOGLE_PRIVATE_KEY_ID',
            'GOOGLE_PRIVATE_KEY',
            'GOOGLE_CLIENT_EMAIL',
            'GOOGLE_CLIENT_ID'
        ]
        
        return all(getattr(cls, var) for var in required_google_vars)
    
    @classmethod
    def get_google_credentials_dict(cls):
        """Build Google credentials dictionary from environment variables"""
        if not cls.has_google_env_credentials():
            return None
        
        return {
            "type": cls.GOOGLE_TYPE,
            "project_id": cls.GOOGLE_PROJECT_ID,
            "private_key_id": cls.GOOGLE_PRIVATE_KEY_ID,
            "private_key": cls.GOOGLE_PRIVATE_KEY,
            "client_email": cls.GOOGLE_CLIENT_EMAIL,
            "client_id": cls.GOOGLE_CLIENT_ID,
            "auth_uri": cls.GOOGLE_AUTH_URI,
            "token_uri": cls.GOOGLE_TOKEN_URI,
            "auth_provider_x509_cert_url": cls.GOOGLE_AUTH_PROVIDER_X509_CERT_URL,
            "client_x509_cert_url": cls.GOOGLE_CLIENT_X509_CERT_URL,
            "universe_domain": cls.GOOGLE_UNIVERSE_DOMAIN
        }

# Example environment variables for reference
EXAMPLE_ENV_VARS = """
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Trello API Configuration
TRELLO_API_KEY=your_trello_api_key_here
TRELLO_TOKEN=your_trello_token_here
TRELLO_BOARD_ID=your_trello_board_id_here

# Google API Configuration (Service Account Environment Variables)
GOOGLE_TYPE=service_account
GOOGLE_PROJECT_ID=your_project_id_here
GOOGLE_PRIVATE_KEY_ID=your_private_key_id_here
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\nyour_private_key_content_here\\n-----END PRIVATE KEY-----\\n"
GOOGLE_CLIENT_EMAIL=your_service_account_email_here
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
GOOGLE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your_service_account_email_encoded_here
GOOGLE_UNIVERSE_DOMAIN=googleapis.com

# Optional: Set to True for verbose logging
VERBOSE=False
""" 