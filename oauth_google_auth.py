"""
OAuth-based Google Authentication Module
Provides user authentication for Google Docs/Drive without requiring document sharing
"""

import os
import logging
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle

logger = logging.getLogger(__name__)

class OAuthGoogleAuth:
    """Handles OAuth authentication for Google services"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/documents.readonly',
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive.file'
    ]
    
    def __init__(self, credentials_file: str = 'credentials.json', token_file: str = 'token.pickle'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = None
        self.docs_service = None
        self.drive_service = None
        
    def authenticate(self) -> bool:
        """
        Authenticate using OAuth flow
        Returns True if authentication successful, False otherwise
        """
        try:
            # Check if we have valid cached credentials
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)
                    
            # If there are no (valid) credentials available, let the user log in
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    try:
                        self.creds.refresh(Request())
                        logger.info("✅ Refreshed Google OAuth credentials")
                    except Exception as e:
                        logger.warning(f"Failed to refresh credentials: {e}")
                        self.creds = None
                        
                if not self.creds:
                    if not os.path.exists(self.credentials_file):
                        logger.error(f"❌ OAuth credentials file not found: {self.credentials_file}")
                        return False
                        
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                    logger.info("✅ Completed Google OAuth authentication")
                    
                # Save the credentials for the next run
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.creds, token)
                    
            # Build the services
            self.docs_service = build('docs', 'v1', credentials=self.creds)
            self.drive_service = build('drive', 'v3', credentials=self.creds)
            
            logger.info("✅ Google OAuth services initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ OAuth authentication failed: {e}")
            return False
            
    def get_document_content(self, document_id: str) -> Optional[str]:
        """
        Get Google Doc content using OAuth authentication
        No sharing required - user must have access to the document
        """
        try:
            if not self.docs_service:
                logger.error("❌ Google Docs service not initialized")
                return None
                
            # Get the document
            document = self.docs_service.documents().get(documentId=document_id).execute()
            
            # Extract text content
            content = []
            for element in document.get('body', {}).get('content', []):
                if 'paragraph' in element:
                    paragraph = element['paragraph']
                    for text_run in paragraph.get('elements', []):
                        if 'textRun' in text_run:
                            content.append(text_run['textRun']['content'])
                            
            full_content = ''.join(content)
            logger.info(f"✅ Successfully retrieved document content ({len(full_content)} characters)")
            return full_content
            
        except Exception as e:
            logger.error(f"❌ Failed to get document content: {e}")
            return None
            
    def extract_document_id(self, url_or_id: str) -> Optional[str]:
        """Extract document ID from Google Docs URL or return ID if already provided"""
        if not url_or_id:
            return None
            
        # If it's already just an ID (no slashes or dots), return it
        if '/' not in url_or_id and '.' not in url_or_id:
            return url_or_id
            
        # Extract from full URL
        if 'docs.google.com' in url_or_id:
            try:
                # Pattern: https://docs.google.com/document/d/DOCUMENT_ID/edit
                parts = url_or_id.split('/')
                doc_index = parts.index('d')
                return parts[doc_index + 1]
            except (ValueError, IndexError):
                logger.error(f"❌ Could not extract document ID from URL: {url_or_id}")
                return None
                
        return url_or_id

# Global OAuth authenticator instance
oauth_auth = OAuthGoogleAuth() 