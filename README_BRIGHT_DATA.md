# Bright Data API Integration for Google Scholar Research Agent

This document explains how to use the Bright Data API integration to bypass CAPTCHAs when searching Google Scholar.

## What is Bright Data?

Bright Data is a premium web scraping platform that provides advanced web unlocker services to bypass CAPTCHAs, IP blocks, and other anti-bot measures. It's particularly effective for accessing Google Scholar and other protected sites.

## Features

- **Automatic CAPTCHA Bypass**: Handles reCAPTCHA v2/v3, FunCaptcha, and other challenges
- **IP Rotation**: Uses residential and datacenter proxies
- **High Success Rate**: Professional-grade infrastructure for reliable access
- **Priority Integration**: Bright Data is tried first before other CAPTCHA solvers

## Setup Instructions

### 1. Get a Bright Data API Key

1. Sign up for a Bright Data account at [brightdata.com](https://brightdata.com)
2. Navigate to your dashboard
3. Create a new zone (recommended: "web_unlocker1")
4. Get your API key from the dashboard

### 2. Set Environment Variables

Set your API key as an environment variable:

```bash
export BRIGHT_DATA_API_KEY="your_bright_data_api_key_here"
export OPENAI_API_KEY="your_openai_api_key_here"
```

### 3. Basic Usage

```python
from google_scholar_research_agent import GoogleScholarResearchAgent

# Initialize the agent
agent = GoogleScholarResearchAgent()

# Configure Bright Data API
agent.configure_bright_data_api(
    enable_bright_data=True,
    api_key="your_api_key",  # Optional if set in environment
    zone="web_unlocker1",    # Your Bright Data zone
    request_timeout=60,      # Request timeout in seconds
    max_retries=3           # Maximum retry attempts
)

# Perform search with automatic CAPTCHA bypass
papers = agent.search_google_scholar([
    "machine learning algorithms",
    "neural network optimization"
])
```

## Configuration Options

### `configure_bright_data_api()` Parameters

- **`enable_bright_data`** (bool): Enable/disable Bright Data API (default: True)
- **`api_key`** (str): Your Bright Data API key (reads from env if not provided)
- **`zone`** (str): Bright Data zone to use (default: "web_unlocker1")
- **`request_timeout`** (int): Request timeout in seconds (default: 60)
- **`max_retries`** (int): Maximum retry attempts (default: 3)

### Example Configuration

```python
# Basic configuration
agent.configure_bright_data_api(
    enable_bright_data=True,
    zone="web_unlocker1"
)

# Advanced configuration
agent.configure_bright_data_api(
    enable_bright_data=True,
    api_key="your_api_key",
    zone="web_unlocker1",
    request_timeout=90,
    max_retries=5
)
```

## How It Works

1. **Priority Order**: When CAPTCHAs are detected, the system tries:
   - Bright Data API (first priority)
   - Enhanced CAPTCHA solver (AzCaptcha, etc.)
   - Basic web-based solver (fallback)

2. **Automatic Detection**: The system automatically detects CAPTCHA blocks and switches to Bright Data

3. **Content Validation**: Responses are validated to ensure successful CAPTCHA bypass

4. **Retry Logic**: Failed requests are retried with exponential backoff

## Example Script

Run the included example script:

```bash
python bright_data_example.py
```

This script demonstrates:
- Environment variable setup
- Agent initialization
- Bright Data configuration
- Sample searches with CAPTCHA bypass
- Result processing

## API Request Format

The integration uses this Bright Data API format:

```python
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "zone": "web_unlocker1",
    "url": "https://scholar.google.com/scholar?q=your_query",
    "format": "raw",
    "method": "GET"
}

response = requests.post(
    "https://api.brightdata.com/request",
    json=data,
    headers=headers
)
```

## Error Handling

The system includes comprehensive error handling:

- **Invalid API Key**: Logs warning and falls back to other methods
- **Network Errors**: Retries with exponential backoff
- **CAPTCHA Detection**: Automatically switches to Bright Data
- **Rate Limiting**: Implements intelligent delays

## Cost Optimization

- **Smart Retry Logic**: Avoids unnecessary API calls
- **Content Validation**: Ensures successful requests before proceeding
- **Fallback System**: Uses cheaper alternatives when possible
- **Priority-Based Usage**: High-priority queries get more resources

## Troubleshooting

### Common Issues

1. **API Key Issues**
   ```
   Error: Bright Data API not configured
   Solution: Set BRIGHT_DATA_API_KEY environment variable
   ```

2. **Network Timeouts**
   ```
   Error: Request timeout
   Solution: Increase request_timeout parameter
   ```

3. **Rate Limiting**
   ```
   Error: Too many requests
   Solution: Increase delays between requests
   ```

### Debug Mode

Enable debug logging to see detailed API interactions:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Best Practices

1. **Environment Variables**: Always use environment variables for API keys
2. **Timeout Settings**: Set appropriate timeouts based on your needs
3. **Retry Logic**: Configure retries based on your reliability requirements
4. **Cost Monitoring**: Monitor API usage to control costs
5. **Fallback Methods**: Keep other CAPTCHA solvers enabled as backups

## Integration with Other Features

The Bright Data API works seamlessly with:
- Enhanced CAPTCHA solver (AzCaptcha)
- Priority-based search
- Paper download and analysis
- Google Docs integration
- Multi-threaded processing

## Performance Metrics

Track performance with built-in statistics:

```python
stats = agent.get_captcha_solver_stats()
print(f"Success rate: {stats.get('success_rate', 'N/A')}")
print(f"Average solve time: {stats.get('avg_solve_time', 'N/A')}")
```

## Support

For issues with this integration:
1. Check your API key and configuration
2. Verify network connectivity
3. Review the logs for specific error messages
4. Contact Bright Data support for API-related issues

For Bright Data API documentation and support:
- [Bright Data Documentation](https://docs.brightdata.com/)
- [API Reference](https://docs.brightdata.com/api-reference)
- [Support Portal](https://help.brightdata.com/)

## Example Output

When working correctly, you'll see logs like:

```
🌐 Bright Data API key found in environment
✅ Bright Data API configured:
  🌐 Zone: web_unlocker1
  ⏱️ Timeout: 60s
  🔄 Max retries: 3
  🔓 Web unlocker enabled for CAPTCHA bypass
🔍 Searching Google Scholar via Bright Data: machine learning
✅ Found 15 papers via Bright Data
```

This indicates successful CAPTCHA bypass and data extraction. 