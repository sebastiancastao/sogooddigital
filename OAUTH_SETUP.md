# OAuth Google Authentication Setup

This guide will help you set up OAuth authentication for Google Docs access, which eliminates the need to share documents with service accounts.

## Why OAuth is Better

- ✅ **No sharing required**: Access any Google Doc you have permission to view
- ✅ **User-based authentication**: Uses your own Google account
- ✅ **More secure**: No service account credentials to manage
- ✅ **Easier setup**: One-time authentication flow

## Setup Steps

### 1. Create Google Cloud Project (if you don't have one)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### 2. Enable Required APIs

Enable these APIs in your Google Cloud Console:
- Google Docs API
- Google Drive API

Navigate to **APIs & Services > Library** and search for each API.

### 3. Create OAuth 2.0 Credentials

1. Go to **APIs & Services > Credentials**
2. Click **+ CREATE CREDENTIALS > OAuth client ID**
3. Choose **Desktop application** as the application type
4. Give it a name (e.g., "AI Content Generator")
5. Click **Create**

### 4. Download Credentials

1. After creating the OAuth client, click the download button
2. Save the file as `credentials.json` in your project root directory
3. The file should look like this:

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

### 5. First Authentication

1. Start your application with the new OAuth setup
2. When you first try to access a Google Doc, a browser window will open
3. Sign in with your Google account
4. Grant permissions to access Google Docs and Drive
5. The application will save a `token.pickle` file for future use

## File Structure

Your project should have these files:
```
your-project/
├── credentials.json          # OAuth credentials (from Google Console)
├── token.pickle             # Generated after first auth (auto-created)
├── oauth_google_auth.py     # OAuth authentication module
└── app.py                   # Main application
```

## Using the OAuth System

Once set up, you can:

1. **Use Google Docs URLs directly**: 
   - `https://docs.google.com/document/d/YOUR_DOC_ID/edit`
   
2. **Use document IDs**: 
   - `YOUR_DOC_ID`

3. **No sharing required**: 
   - Any document you can view in Google Docs will work
   - No need to share with service account emails

## Troubleshooting

### Browser doesn't open during authentication
- Make sure port 8080 is available
- Try running the application with administrator privileges

### "File not found" error
- Ensure `credentials.json` is in the project root
- Check that the file was downloaded correctly from Google Console

### Permission denied errors
- Make sure you granted all requested permissions during OAuth flow
- Delete `token.pickle` and re-authenticate if needed

### Invalid credentials
- Check that you enabled Google Docs API and Google Drive API
- Verify the OAuth client is configured for "Desktop application"

## Security Notes

- Keep `credentials.json` secure and don't commit it to public repositories
- The `token.pickle` file contains your access tokens - also keep it secure
- Tokens are automatically refreshed when they expire

## Benefits Over Service Account

| Feature | OAuth | Service Account |
|---------|-------|-----------------|
| Document sharing | ❌ Not required | ✅ Required |
| Setup complexity | 🟡 Medium | 🔴 High |
| User permissions | ✅ Uses your access | ❌ Limited to shared docs |
| Security | ✅ User-based | 🟡 Service-based |
| Maintenance | ✅ Auto-refresh | ❌ Manual key management |

The OAuth approach is much more user-friendly and doesn't require document sharing! 