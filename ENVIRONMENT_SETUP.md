# Environment Variables Setup Guide

This document lists all the environment variables you need to configure for your SoGoodDigital project.

## Required Environment Variables

### 1. Bright Data API (Required)
```bash
BRIGHT_DATA_API_KEY=your_bright_data_api_key_here
```
**How to get it:**
- Sign up at https://brightdata.com/
- Go to your dashboard and create a new zone
- Copy the API key from your zone configuration

### 2. OpenAI API (Optional - for AI features)
```bash
OPENAI_API_KEY=your_openai_api_key_here
```
**How to get it:**
- Sign up at https://platform.openai.com/
- Go to API Keys section
- Create a new secret key
- Copy the key (starts with 'sk-')

## Optional Environment Variables

### 3. Trello Integration (Optional - for task management)
```bash
TRELLO_API_KEY=your_trello_api_key_here
TRELLO_TOKEN=your_trello_token_here
TRELLO_BOARD_ID=your_trello_board_id_here
```
**How to get them:**
- Go to https://trello.com/app-key
- Copy your API Key
- Generate a Token (click the Token link)
- Get your Board ID from the board URL

### 4. Google API Configuration (Optional - for Google services)
```bash
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.pickle
```
**How to set up:**
- Go to Google Cloud Console
- Create a new project or select existing one
- Enable the APIs you need (Google Sheets, Drive, etc.)
- Create service account credentials
- Download the JSON file and rename it to `credentials.json`

### 5. Logging Configuration
```bash
VERBOSE=false
```
**Options:**
- `true` - Enable verbose logging
- `false` - Normal logging level

## Setup Methods

### Method 1: Create .env file (Recommended)
Create a `.env` file in your project root with all variables:

```bash
# Bright Data API (Required)
BRIGHT_DATA_API_KEY=your_bright_data_api_key_here

# OpenAI API (Optional)
OPENAI_API_KEY=your_openai_api_key_here

# Trello Integration (Optional)
TRELLO_API_KEY=your_trello_api_key_here
TRELLO_TOKEN=your_trello_token_here
TRELLO_BOARD_ID=your_trello_board_id_here

# Google API Configuration (Optional)
GOOGLE_CREDENTIALS_FILE=credentials.json
GOOGLE_TOKEN_FILE=token.pickle

# Logging Configuration
VERBOSE=false
```

### Method 2: Export commands (for current session)
```bash
# Required
export BRIGHT_DATA_API_KEY="your_bright_data_api_key_here"

# Optional
export OPENAI_API_KEY="your_openai_api_key_here"
export TRELLO_API_KEY="your_trello_api_key_here"
export TRELLO_TOKEN="your_trello_token_here"
export TRELLO_BOARD_ID="your_trello_board_id_here"
export GOOGLE_CREDENTIALS_FILE="credentials.json"
export GOOGLE_TOKEN_FILE="token.pickle"
export VERBOSE="false"
```

### Method 3: PowerShell (Windows)
```powershell
# Required
$env:BRIGHT_DATA_API_KEY="your_bright_data_api_key_here"

# Optional
$env:OPENAI_API_KEY="your_openai_api_key_here"
$env:TRELLO_API_KEY="your_trello_api_key_here"
$env:TRELLO_TOKEN="your_trello_token_here"
$env:TRELLO_BOARD_ID="your_trello_board_id_here"
$env:GOOGLE_CREDENTIALS_FILE="credentials.json"
$env:GOOGLE_TOKEN_FILE="token.pickle"
$env:VERBOSE="false"
```

## Quick Start (Minimum Required)

To get started quickly, you only need:

```bash
BRIGHT_DATA_API_KEY=your_bright_data_api_key_here
```

All other variables are optional and only needed for specific features:
- **OpenAI**: For AI-powered marketing analysis and research
- **Trello**: For task management features
- **Google API**: For Google Sheets/Drive integration

## Security Notes

⚠️ **IMPORTANT SECURITY REMINDERS:**

1. **Never commit API keys to git**
2. **Use `.env` files and add them to `.gitignore`**
3. **Keep your API keys secret and secure**
4. **Regenerate keys if they're ever exposed**
5. **Use environment variables in production**

## Troubleshooting

If you see errors about missing environment variables:

1. Check that your `.env` file exists in the project root
2. Verify the variable names are spelled correctly
3. Make sure there are no extra spaces around the `=` sign
4. Restart your terminal/application after setting variables

## Testing Your Setup

Run this command to test if your environment is configured correctly:
```bash
python setup_check.py
```

This will verify that all required variables are set and accessible. 