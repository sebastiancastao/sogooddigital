# Task Assigner - Google Docs to Trello Integration

This Python application processes Google Docs content using OpenAI, extracts actionable tasks, assigns them to team members based on their responsibilities, and creates Trello cards automatically.

## Team Responsibilities

The system automatically assigns tasks based on these team member responsibilities:

- **Rana**: Oversees all social media, including both organic planning and paid ad strategy. Coordinates with graphic designers and content creators.
- **Scott**: Leads written content and content strategy, covering blogs, case studies, and SEO from a PR and visibility perspective.
- **Sebastian**: Supports day-to-day SEO tasks, metadata updates, and assists with task management or research.
- **Ilia**: Provides strategic oversight and supports where cross-team input is needed.

## Features

- 📄 **Google Docs Integration**: Extracts text content from Google Docs
- 🤖 **AI-Powered Task Extraction**: Uses OpenAI GPT-4o to identify and structure tasks
- 👥 **Smart Assignment**: Automatically assigns tasks to team members based on content analysis
- 📋 **Trello Integration**: Creates cards with detailed task information
- 🔍 **Keyword Matching**: Uses intelligent keyword matching for accurate assignments
- 📊 **Detailed Reporting**: Provides comprehensive results and error reporting

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Google Cloud Project with Docs API enabled
- Trello API key and token
- Trello board ID

## Installation

1. Clone or download the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### 1. Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Trello API Configuration
TRELLO_API_KEY=your_trello_api_key_here
TRELLO_TOKEN=your_trello_token_here
TRELLO_BOARD_ID=your_trello_board_id_here

# Optional: Set to True for verbose logging
VERBOSE=False
```

### 2. Google API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Docs API
4. Create credentials (OAuth 2.0 client ID)
5. Download the credentials file and save it as `credentials.json` in the project root

### 3. Trello Setup

1. Get your Trello API key from [https://trello.com/app-key](https://trello.com/app-key)
2. Generate a token using the link provided on the API key page
3. Find your board ID by going to your Trello board and looking at the URL:
   ```
   https://trello.com/b/BOARD_ID/board-name
   ```

## Usage

### Command Line

```bash
python task_assigner.py DOC_ID [--verbose]
```

**Example:**
```bash
python task_assigner.py 1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

### Programmatic Usage

```python
from task_assigner import TaskAssigner

# Initialize the assigner
assigner = TaskAssigner()

# Process a Google Doc
doc_id = "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
results = assigner.process_google_doc(doc_id)

# Check results
print(f"Total tasks: {results['total_tasks']}")
print(f"Trello cards created: {len(results['trello_cards'])}")
```

## How It Works

1. **Document Processing**: Extracts text content from the specified Google Doc
2. **AI Analysis**: Sends content to OpenAI GPT-4o to extract structured tasks
3. **Assignment Logic**: Analyzes task content and assigns to team members based on:
   - Keyword matching with team member responsibilities
   - Task category analysis
   - Content context evaluation
4. **Trello Integration**: Creates cards with:
   - Task title and description
   - Assigned team member
   - Priority and effort estimates
   - Due dates (if specified)
   - Requirements and dependencies

## Task Assignment Logic

The system uses a sophisticated keyword matching algorithm:

- **Rana**: Tasks related to social media, campaigns, graphic design, content creation
- **Scott**: Tasks involving content strategy, writing, blogs, PR, visibility
- **Sebastian**: Tasks about SEO, metadata, analytics, research, task management
- **Ilia**: Strategic tasks, cross-team coordination, planning, oversight

## Output Format

The application returns a dictionary with:
- `total_tasks`: Number of tasks extracted
- `assignments`: Task count per team member
- `trello_cards`: List of created cards with URLs
- `errors`: Any errors encountered during processing

## Error Handling

The application includes comprehensive error handling for:
- API authentication failures
- Network connectivity issues
- Invalid document IDs
- Malformed content
- Trello board access issues

## Logging

Enable verbose logging with the `--verbose` flag or set `VERBOSE=True` in your environment variables.

## Dependencies

- `openai`: OpenAI API client
- `google-api-python-client`: Google APIs client
- `google-auth-*`: Google authentication
- `requests`: HTTP requests for Trello API
- `python-dotenv`: Environment variable management

## Troubleshooting

### Common Issues

1. **Google API Authentication**: Ensure `credentials.json` is in the project root
2. **Trello Access**: Verify board ID and API permissions
3. **OpenAI API**: Check API key and usage limits
4. **Document Access**: Ensure the Google Doc is accessible with your credentials

### Debug Mode

Run with verbose logging to see detailed processing steps:
```bash
python task_assigner.py DOC_ID --verbose
```

## License

This project is provided as-is for internal use. Please ensure you comply with all relevant API terms of service.

## Support

For issues or questions, please check the error logs and ensure all configuration is correct as described in this README. 