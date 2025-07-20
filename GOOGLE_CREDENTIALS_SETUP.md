# Google API Credentials Setup Guide

## Overview
This guide will help you create the `credentials.json` file needed for the Google Scholar Research Agent to access Google Docs and Drive APIs.

## Prerequisites
- Google account
- Access to Google Cloud Console

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" or the project dropdown
3. Click "New Project"
4. Enter a project name (e.g., "research-agent-project")
5. Click "Create"

## Step 2: Enable Required APIs

1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for and enable the following APIs:
   - **Google Docs API**
   - **Google Drive API**

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in the required fields:
     - App name: "Research Agent"
     - User support email: Your email
     - Developer contact: Your email
   - Add scopes:
     - `https://www.googleapis.com/auth/documents`
     - `https://www.googleapis.com/auth/drive.readonly`
     - `https://www.googleapis.com/auth/drive.file`
4. For OAuth client ID:
   - Application type: "Desktop application"
   - Name: "Research Agent Desktop"
5. Click "Create"
6. Download the JSON file and rename it to `credentials.json`

## Step 4: Place the Credentials File

1. Place the `credentials.json` file in your project root directory
2. Make sure the file is in the same directory as your Python scripts

## Step 5: Test the Setup

The application will prompt you to authenticate the first time you run it. This will:
1. Open a browser window
2. Ask you to sign in to Google
3. Request permission to access your Google Docs and Drive
4. Create a `token.json` file for future use

## Security Notes

- Never commit `credentials.json` to version control
- Keep your credentials secure
- Add `credentials.json` and `token.json` to your `.gitignore` file

## Example credentials.json Structure

```json
{
  "installed": {
    "client_id": "your-client-id.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "your-client-secret",
    "redirect_uris": ["http://localhost"]
  }
}
```

## Troubleshooting

### Common Issues:
1. **API not enabled**: Make sure you've enabled both Google Docs and Drive APIs
2. **OAuth consent screen**: Complete the consent screen configuration
3. **Scopes mismatch**: Ensure all required scopes are added
4. **File location**: Verify `credentials.json` is in the correct directory

### Error Messages:
- "The OAuth client was not found": Check your client ID and project
- "Access blocked": Complete OAuth consent screen setup
- "Invalid scope": Verify all required scopes are enabled

## Next Steps

Once you have your `credentials.json` file:
1. Run the application
2. Complete the OAuth flow in your browser
3. The application will create a `token.json` file for future use
4. You can now use Google Docs and Drive features

## Support

If you encounter issues:
1. Check the Google Cloud Console for any error messages
2. Verify your project has the necessary APIs enabled
3. Ensure your OAuth consent screen is properly configured
4. Review the scopes and permissions 
 