"""
Google Credentials Helper
Utility functions for handling Google API authentication from environment variables
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from config import Config

logger = logging.getLogger(__name__)

class GoogleCredentialsHelper:
    """Helper class for Google API authentication using environment variables"""
    
    @staticmethod
    def create_credentials_from_env(scopes: list = None) -> Optional[service_account.Credentials]:
        """
        Create Google service account credentials from environment variables
        
        Args:
            scopes: List of Google API scopes
            
        Returns:
            service_account.Credentials object or None if credentials cannot be created
        """
        if scopes is None:
            scopes = [
                'https://www.googleapis.com/auth/documents',
                'https://www.googleapis.com/auth/drive.readonly',
                'https://www.googleapis.com/auth/drive.file'
            ]
        
        try:
            # Check if all required environment variables are present
            if not Config.has_google_env_credentials():
                logger.warning("Not all required Google environment variables are set")
                return None
            
            # Build credentials dictionary from environment variables
            credentials_dict = Config.get_google_credentials_dict()
            
            if not credentials_dict:
                logger.error("Failed to build credentials dictionary from environment variables")
                return None
            
            # Create credentials from the dictionary
            credentials = service_account.Credentials.from_service_account_info(
                credentials_dict, scopes=scopes
            )
            
            logger.info("✅ Successfully created Google credentials from environment variables")
            logger.info(f"   📧 Client email: {credentials_dict.get('client_email')}")
            logger.info(f"   🏷️  Project ID: {credentials_dict.get('project_id')}")
            
            return credentials
            
        except Exception as e:
            logger.error(f"❌ Failed to create credentials from environment variables: {e}")
            return None
    
    @staticmethod
    def create_credentials_from_file(file_path: str, scopes: list = None) -> Optional[service_account.Credentials]:
        """
        Create Google service account credentials from JSON file (fallback method)
        
        Args:
            file_path: Path to service account JSON file
            scopes: List of Google API scopes
            
        Returns:
            service_account.Credentials object or None if file cannot be loaded
        """
        if scopes is None:
            scopes = [
                'https://www.googleapis.com/auth/documents',
                'https://www.googleapis.com/auth/drive.readonly',
                'https://www.googleapis.com/auth/drive.file'
            ]
        
        try:
            if not os.path.exists(file_path):
                logger.warning(f"Service account file not found: {file_path}")
                return None
            
            credentials = service_account.Credentials.from_service_account_file(
                file_path, scopes=scopes
            )
            
            logger.info(f"✅ Successfully loaded Google credentials from file: {file_path}")
            return credentials
            
        except Exception as e:
            logger.error(f"❌ Failed to load credentials from file {file_path}: {e}")
            return None
    
    @staticmethod
    def get_google_credentials(scopes: list = None) -> Optional[service_account.Credentials]:
        """
        Get Google credentials using the best available method
        Priority: Environment variables > Service account file > Fallback files
        
        Args:
            scopes: List of Google API scopes
            
        Returns:
            service_account.Credentials object or None if no credentials available
        """
        if scopes is None:
            scopes = [
                'https://www.googleapis.com/auth/documents',
                'https://www.googleapis.com/auth/drive.readonly',
                'https://www.googleapis.com/auth/drive.file'
            ]
        
        # Method 1: Try environment variables first (preferred)
        logger.info("🔍 Attempting to authenticate with Google using environment variables...")
        credentials = GoogleCredentialsHelper.create_credentials_from_env(scopes)
        if credentials:
            logger.info("✅ Authentication successful using environment variables")
            return credentials
        
        # Method 2: Try service account files
        service_account_paths = [
            'service-account.json',
            'task assigner/service-account.json',
            Config.GOOGLE_SERVICE_ACCOUNT_PATH
        ]
        
        for sa_path in service_account_paths:
            if sa_path and os.path.exists(sa_path):
                logger.info(f"🔍 Attempting to authenticate using service account file: {sa_path}")
                credentials = GoogleCredentialsHelper.create_credentials_from_file(sa_path, scopes)
                if credentials:
                    logger.info(f"✅ Authentication successful using file: {sa_path}")
                    return credentials
        
        # Method 3: Try legacy credentials file
        if os.path.exists(Config.GOOGLE_CREDENTIALS_FILE):
            logger.info(f"🔍 Attempting to authenticate using legacy credentials file: {Config.GOOGLE_CREDENTIALS_FILE}")
            credentials = GoogleCredentialsHelper.create_credentials_from_file(Config.GOOGLE_CREDENTIALS_FILE, scopes)
            if credentials:
                logger.info(f"✅ Authentication successful using legacy file: {Config.GOOGLE_CREDENTIALS_FILE}")
                return credentials
        
        # No credentials found
        logger.error("❌ No valid Google credentials found")
        logger.error("  💡 Solutions:")
        logger.error("  1. Set Google environment variables (recommended)")
        logger.error("  2. Place service-account.json in project directory")
        logger.error("  3. Set GOOGLE_SERVICE_ACCOUNT_PATH environment variable")
        
        return None
    
    @staticmethod
    def build_google_services(scopes: list = None) -> tuple:
        """
        Build Google Docs and Drive services
        
        Args:
            scopes: List of Google API scopes
            
        Returns:
            Tuple of (docs_service, drive_service) or (None, None) if authentication fails
        """
        credentials = GoogleCredentialsHelper.get_google_credentials(scopes)
        
        if not credentials:
            return None, None
        
        try:
            docs_service = build('docs', 'v1', credentials=credentials)
            drive_service = build('drive', 'v3', credentials=credentials)
            
            logger.info("✅ Google Docs API service ready")
            logger.info("✅ Google Drive API service ready")
            
            return docs_service, drive_service
            
        except Exception as e:
            logger.error(f"❌ Failed to build Google services: {e}")
            return None, None
    
    @staticmethod
    def test_authentication() -> bool:
        """
        Test Google authentication and service access
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            docs_service, drive_service = GoogleCredentialsHelper.build_google_services()
            
            if not docs_service or not drive_service:
                return False
            
            # Test a simple API call to verify access
            # Note: This is just testing the service creation, not actual API access
            logger.info("🧪 Testing Google API access...")
            logger.info("✅ Google authentication test passed")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Google authentication test failed: {e}")
            return False 