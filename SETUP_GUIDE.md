# Setup Guide for AI Document Generator & Google Scholar Research Agent

This guide will walk you through setting up both the AI Document Generator and Google Scholar Research Agent on your system.

## Prerequisites 📋

- Python 3.7 or higher
- A computer with internet connection
- Basic familiarity with command line/terminal
- OpenAI API account (for both tools)
- Google Cloud Console account (for Google Scholar Research Agent)

## Step 1: Install Python and Dependencies 🐍

### 1.1 Verify Python Installation
```bash
python --version
# or
python3 --version
```

If Python is not installed, download it from [python.org](https://www.python.org/downloads/).

### 1.2 Install Required Packages
```bash
# Navigate to your project directory
cd /path/to/your/project

# Install all required packages
pip install -r requirements.txt
```

If you encounter permission errors, try:
```bash
pip install --user -r requirements.txt
```

### 1.3 Download NLP Models (AUTOMATIC) 🧠
The Google Scholar Research Agent will automatically download required NLP models when first run:

- **spaCy English model** - Downloads automatically if not found
- **NLTK data** - Downloads automatically when first used

If you want to download the spaCy model manually:
```bash
python -m spacy download en_core_web_sm
```

⚠️ **Note**: If you see "spaCy model not found" warnings, the system will attempt automatic download. Ensure you have internet connection on first run.

## Step 2: Set Up OpenAI API 🤖

### 2.1 Create OpenAI Account
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up for an account or log in
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy the generated key (starts with `sk-`)

### 2.2 Configure Environment Variables
1. Create a `.env` file in your project directory:
   ```bash
   touch .env
   ```

2. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

3. (Optional) Add other OpenAI configurations:
   ```
   OPENAI_MODEL=gpt-4
   OPENAI_MAX_TOKENS=4000
   OPENAI_TEMPERATURE=0.3
   ```

## Step 3: Set Up Google APIs (For Google Scholar Research Agent) 🔍

### 3.1 Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click "Select a project" → "New Project"
4. Enter a project name (e.g., "research-agent")
5. Click "Create"

### 3.2 Enable Required APIs
1. In the Google Cloud Console, navigate to "APIs & Services" → "Library"
2. Search for and enable the following APIs:
   - **Google Docs API**
   - **Google Drive API**
   - **Google Sheets API** (optional, for future features)

### 3.3 Create Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in required fields (App name, User support email, Developer contact)
   - Add your email to test users
   - Save and continue through all steps
4. Back in Credentials, create OAuth client ID:
   - Application type: "Desktop application"
   - Name: "Research Agent"
   - Click "Create"
5. Download the credentials JSON file
6. Rename it to `credentials.json` and place it in your project directory

### 3.4 Set Up OAuth Consent Screen
1. Go to "APIs & Services" → "OAuth consent screen"
2. Add required information:
   - App name: "Google Scholar Research Agent"
   - User support email: your email
   - Developer contact: your email
3. Add scopes (if prompted):
   - `https://www.googleapis.com/auth/documents`
   - `https://www.googleapis.com/auth/drive.readonly`
   - `https://www.googleapis.com/auth/drive.file`
4. Add test users (your email address)
5. Save and continue

## Step 4: Verify Installation 🔍

### 4.1 Test AI Document Generator
```bash
python -c "from ai_document_generator import AIDocumentGenerator; print('AI Document Generator imported successfully')"
```

### 4.2 Test Google Scholar Research Agent
```bash
python -c "from google_scholar_research_agent import GoogleScholarResearchAgent; print('Google Scholar Research Agent imported successfully')"
```

### 4.3 Test spaCy Model
```bash
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('spaCy model loaded successfully')"
```

If this fails, manually download:
```bash
python -m spacy download en_core_web_sm
```

### 4.4 Check Environment Variables
```bash
python -c "import os; print('OpenAI API Key:', 'Found' if os.getenv('OPENAI_API_KEY') else 'Not found')"
```

## Step 5: First Time Setup 🚀

### 5.1 Google Authentication (One-time setup)
When you first run the Google Scholar Research Agent, it will:
1. Open a browser window
2. Ask you to sign in to Google
3. Request permission to access your Google Drive and Docs
4. Create a `token.json` file for future use

This is normal and only happens once.

### 5.2 Test Google File Access
1. Create a test Google Doc
2. Add some content (e.g., "Machine learning applications in healthcare")
3. Get the file ID from the URL:
   ```
   https://docs.google.com/document/d/FILE_ID_HERE/edit
   ```
4. Copy the `FILE_ID_HERE` part

## Step 6: Run Examples 🎯

### 6.1 AI Document Generator Examples
```bash
python example_usage.py
```

This will create several sample documents.

### 6.2 Google Scholar Research Agent Examples
```bash
python google_scholar_example.py
```

This will show an interactive menu with different examples.

## Common Issues and Solutions 🔧

### Issue 1: OpenAI API Key Error
**Error**: `openai.error.AuthenticationError: Incorrect API key`

**Solution**:
- Verify your API key is correct in the `.env` file
- Check that you have sufficient credits in your OpenAI account
- Ensure the API key hasn't expired

### Issue 2: Google Authentication Error
**Error**: `google.auth.exceptions.RefreshError`

**Solution**:
- Delete `token.json` file and re-authenticate
- Check that your `credentials.json` file is in the project directory
- Verify that Google APIs are enabled in your project

### Issue 3: ModuleNotFoundError
**Error**: `ModuleNotFoundError: No module named 'openai'`

**Solution**:
```bash
pip install -r requirements.txt
```

### Issue 4: Permission Denied
**Error**: `PermissionError: [Errno 13] Permission denied`

**Solution**:
```bash
pip install --user -r requirements.txt
```

### Issue 5: spaCy Model Not Found
**Error**: `spaCy model not found. Some features may be limited`

**Solution**:
The system will attempt automatic download. If this fails, manually download:
```bash
python -m spacy download en_core_web_sm
```

If the automatic download fails:
```bash
# Try upgrading spaCy first
pip install --upgrade spacy

# Then download the model
python -m spacy download en_core_web_sm
```

### Issue 6: Rate Limiting
**Error**: `Too many requests` or `Rate limit exceeded`

**Solution**:
- Wait a few minutes and try again
- Reduce the number of search queries
- Check your OpenAI usage limits

## File Structure 📁

After setup, your project directory should look like this:
```
your-project/
├── .env                              # Your API keys
├── credentials.json                  # Google API credentials
├── token.json                       # Generated after first Google auth
├── requirements.txt                 # Python dependencies
├── ai_document_generator.py         # AI Document Generator
├── google_scholar_research_agent.py # Google Scholar Research Agent
├── example_usage.py                 # AI Document Generator examples
├── google_scholar_example.py        # Google Scholar Research Agent examples
├── README.md                        # Project documentation
└── SETUP_GUIDE.md                  # This file
```

## Next Steps 🎯

1. **Start with AI Document Generator**: Run `python example_usage.py` to create your first documents
2. **Try Google Scholar Research Agent**: Run `python google_scholar_example.py` and follow the prompts
3. **Create your own research**: Use your own Google files as input
4. **Customize parameters**: Adjust settings for your specific needs

## Getting Help 🆘

If you encounter issues:

1. **Check the error message**: Most errors provide helpful information
2. **Verify your setup**: Ensure all files are in the correct location
3. **Check API status**: 
   - OpenAI: [status.openai.com](https://status.openai.com/)
   - Google: [status.cloud.google.com](https://status.cloud.google.com/)
4. **Review the documentation**: Both tools have detailed documentation in the README

## Security Best Practices 🔒

1. **Never commit API keys**: Always use `.env` files and add them to `.gitignore`
2. **Monitor usage**: Check your OpenAI usage regularly
3. **Use minimal permissions**: Only enable required Google API scopes
4. **Keep credentials secure**: Don't share your `credentials.json` or `token.json` files
5. **Regular updates**: Keep your dependencies updated

## Tips for Success 💡

1. **Start small**: Begin with simple examples before complex research
2. **Test incrementally**: Verify each step works before moving to the next
3. **Read the prompts**: The agents use advanced prompting techniques - understanding them helps
4. **Be patient**: Research analysis can take time, especially for large document sets
5. **Iterate**: Refine your inputs based on the outputs you receive

---

**Congratulations! 🎉** You're now ready to use both the AI Document Generator and Google Scholar Research Agent. Start with the examples and gradually work your way up to more complex use cases.

For additional help, refer to the main README.md file or check the example scripts. 