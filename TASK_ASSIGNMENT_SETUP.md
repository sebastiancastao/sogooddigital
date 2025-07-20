# Task Assignment Integration Setup Guide

## Overview

The task assignment functionality has been successfully integrated into your Flask app. This feature allows you to:

- Extract actionable tasks from Google Docs using AI
- Automatically assign tasks to team members based on their expertise
- Create Trello cards with detailed task information
- Track progress in real-time

## Quick Start

1. **Access the Feature**: Navigate to `/tasks` in your Flask app or click "Task Assignment" in the navigation
2. **Enter Google Doc ID**: Paste the document ID from a Google Docs URL
3. **Start Processing**: Click "Assign Tasks" and watch real-time progress
4. **View Results**: See extracted tasks, assignments, and created Trello cards

## Configuration Required

### 1. Environment Variables

Create a `.env.local` file in your project root with these variables:

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-here-change-this-in-production

# OpenAI API Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Google API Configuration (Required)
GOOGLE_CREDENTIALS_FILE=credentials.json

# Trello Integration (Optional but recommended)
TRELLO_API_KEY=your_trello_api_key_here
TRELLO_TOKEN=your_trello_token_here
TRELLO_BOARD_ID=your_trello_board_id_here

# Optional
VERBOSE=False
```

### 2. API Setup Instructions

#### OpenAI API (Required)
1. Sign up at [OpenAI Platform](https://platform.openai.com/)
2. Create an API key in your account settings
3. Add the key to your `.env.local` file

#### Google Docs API (Required)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Google Docs API
3. Create service account credentials OR OAuth 2.0 client ID
4. Download the JSON file and save as `credentials.json` in your project root

#### Trello Integration (Optional)
1. Go to [Trello API Key page](https://trello.com/app-key)
2. Copy your API key
3. Generate a token using the provided link
4. Find your board ID from the board URL: `https://trello.com/b/BOARD_ID/board-name`
5. Add all three values to your `.env.local` file

## Team Assignment Logic

The system automatically assigns tasks based on these team member responsibilities:

### Rana
- **Focus**: Social media, campaigns, graphic design
- **Keywords**: social media, instagram, facebook, organic, paid ads, content planning, etc.

### Scott
- **Focus**: Content strategy, blogs, PR
- **Keywords**: content strategy, blog, writing, case studies, PR, visibility, etc.

### Sebastian
- **Focus**: SEO, analytics, research
- **Keywords**: SEO, metadata, analytics, technical SEO, research, task management, etc.

### Ilia
- **Focus**: Strategy, oversight, coordination
- **Keywords**: strategy, strategic, oversight, cross-team, planning, leadership, etc.

## Files Added/Modified

### New Files
- `task_assignment.py` - Core task assignment functionality
- `templates/task_assignment.html` - Task assignment form page
- `templates/task_progress.html` - Real-time progress tracking
- `templates/task_results.html` - Results display page

### Modified Files
- `app.py` - Added task assignment routes and functionality
- `requirements.txt` - Added Flask and Flask-SocketIO dependencies
- `templates/base.html` - Added navigation link and Tailwind CSS support

## New Routes Available

- `/tasks` - Task assignment form
- `/tasks/assign` (POST) - Start task assignment process
- `/tasks/progress/<task_id>` - Real-time progress tracking
- `/tasks/results/<task_id>` - View assignment results
- `/api/tasks/config` - Check configuration status

## Features

### 🤖 AI-Powered Task Extraction
- Uses OpenAI GPT-4o to analyze document content
- Extracts structured task information including priority, effort, deadlines
- Identifies task categories and requirements

### 🎯 Smart Assignment Algorithm
- Keyword-based matching with team member expertise
- Category-based fallback assignment
- Handles edge cases and unknown task types

### 📋 Trello Integration
- Creates organized Trello cards automatically
- Assigns team members to cards when possible
- Includes detailed task descriptions and metadata

### ⚡ Real-time Progress Tracking
- WebSocket-based live updates
- Step-by-step progress indicators
- Detailed processing logs

### 📊 Comprehensive Results
- Task extraction statistics
- Team assignment breakdown
- Direct links to created Trello cards
- Error reporting and handling

## Usage Examples

### Basic Usage
1. Open Google Doc with actionable content
2. Copy the document ID from the URL
3. Navigate to `/tasks` in your Flask app
4. Paste the document ID and click "Assign Tasks"
5. Watch real-time progress and view results

### Advanced Features
- View configuration status before processing
- Open all Trello cards at once from results page
- Monitor processing details and error logs
- Navigate between different features seamlessly

## Troubleshooting

### Configuration Issues
- Use the configuration checker at `/api/tasks/config`
- Ensure all required environment variables are set
- Verify Google credentials file exists and is accessible

### Google Docs Access
- Make sure the document is accessible with your credentials
- For service accounts, share the document with the service account email
- For OAuth, ensure proper scopes are granted

### Trello Integration
- Verify API key and token are correct
- Ensure board ID is valid and accessible
- Check that your Trello account has permissions to create cards

### Common Errors
- **"No content found"**: Document might be empty or inaccessible
- **"No tasks extracted"**: Content might not contain actionable items
- **"Missing configuration"**: Check environment variables
- **"Trello card creation failed"**: Verify Trello credentials and permissions

## Testing

Test the integration with a sample Google Doc containing:
- Clear action items (e.g., "Create social media campaign for Q4")
- Different types of tasks for various team members
- Priorities and deadlines where applicable
- Dependencies and requirements

## Support

The task assignment feature is now fully integrated with your Flask app and maintains consistency with your existing UI and functionality. All features support real-time updates and error handling.

For issues:
1. Check the configuration status page
2. Review browser console and Flask logs
3. Verify all API credentials are correctly set
4. Ensure required dependencies are installed 