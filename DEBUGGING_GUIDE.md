# Bright Data API Debugging Guide

This guide explains how to debug and test the Bright Data API integration with your Google Scholar research agent.

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)
```bash
# Run the setup script to test everything automatically
python setup_bright_data.py
```

### Option 2: Manual Environment Setup
```bash
# Set environment variable (Linux/Mac)
export BRIGHT_DATA_API_KEY="26ca0b85-c197-4f30-8b44-acb65771f482"

# Or use the provided script
source set_env.sh

# Then run tests
python test_bright_data_debug.py
```

### Option 3: Windows PowerShell
```powershell
# Set environment variable
$env:BRIGHT_DATA_API_KEY="26ca0b85-c197-4f30-8b44-acb65771f482"

# Run tests
python test_bright_data_debug.py
```

## 🔧 Debugging Features Added

### 1. Enhanced Logging
The integration now includes comprehensive logging at multiple levels:

```python
import logging
logging.basicConfig(level=logging.DEBUG)  # Enable debug logging

agent = GoogleScholarResearchAgent()
```

**Log Levels:**
- `INFO`: General operation status
- `DEBUG`: Detailed API calls, content analysis, timing
- `ERROR`: Failed requests, exceptions with stack traces

### 2. Statistics Tracking
Track API performance with built-in statistics:

```python
# Get detailed statistics
stats = agent.get_bright_data_stats()
print(f"Requests made: {stats['requests_made']}")
print(f"Success rate: {stats['success_rate']:.1f}%")
print(f"Average response time: {stats['average_response_time']:.2f}s")
print(f"CAPTCHAs bypassed: {stats['captcha_bypassed']}")
```

### 3. Content Validation
Advanced content checking to ensure CAPTCHA bypass success:

```python
# The system automatically checks for:
# - CAPTCHA indicators ('captcha', 'recaptcha', 'verify you are human')
# - Google Scholar content markers ('cited by', 'gs_r gs_or gs_scl')
# - Content length and quality
# - Block page detection
```

### 4. Request Timing
All requests are timed for performance analysis:

```python
# Response times are automatically logged
# 📈 Response time: 2.34s
# Average response time is tracked in statistics
```

## 🧪 Testing Scripts

### 1. setup_bright_data.py
**Quick setup and basic testing**
- Sets environment variables
- Tests basic API connectivity
- Tests Google Scholar access
- Shows usage examples

```bash
python setup_bright_data.py
```

### 2. test_bright_data_debug.py
**Comprehensive debugging suite**
- Environment validation
- Basic HTTP request testing
- Google Scholar request testing
- Agent integration testing
- Full search pipeline testing

```bash
python test_bright_data_debug.py
```

This creates a detailed log file: `bright_data_debug_YYYYMMDD_HHMMSS.log`

## 🔍 Debug Output Examples

### Successful Request
```
🌐 Making Bright Data request #1
  📍 Target URL: https://scholar.google.com/scholar?q=machine+learning
  🔧 Zone: web_unlocker1
  ⏱️ Timeout: 60s
  📈 Response time: 2.34s
  📊 Status code: 200
✅ Bright Data request successful
  📏 Content length: 45234 characters
🎉 Successfully bypassed CAPTCHA with Bright Data
🔍 Google Scholar content detected: ['scholar.google.com', 'cited by']
```

### Failed Request
```
🌐 Making Bright Data request #1
  📍 Target URL: https://scholar.google.com/scholar?q=test
  🔧 Zone: web_unlocker1
❌ Bright Data request failed: 401
  📄 Response: {"error": "Invalid API key"}
```

### CAPTCHA Detection
```
🔒 Received blocked/CAPTCHA content despite Bright Data
🔍 CAPTCHA indicators found: ['captcha', 'verify you are human']
🔍 Content preview: <html><head><title>Please verify you are human...
```

## 📊 Monitoring Performance

### Real-time Statistics
```python
# Check stats during operation
stats = agent.get_bright_data_stats()
print(f"""
📊 Bright Data Performance:
├── Requests: {stats['requests_made']}
├── Success Rate: {stats['success_rate']:.1f}%
├── Avg Response Time: {stats['average_response_time']:.2f}s
├── CAPTCHAs Bypassed: {stats['captcha_bypassed']}
└── Last Error: {stats['last_error'] or 'None'}
""")
```

### Configuration Status
```python
# Check current configuration
config = agent.bright_data_config
print(f"""
🔧 Configuration:
├── Enabled: {agent.bright_data_enabled}
├── Zone: {config['zone']}
├── Timeout: {config['request_timeout']}s
└── Max Retries: {config['max_retries']}
""")
```

## ⚠️ Common Issues & Solutions

### 1. API Key Issues
**Problem:** `🚨 Bright Data API not configured`
**Solution:** 
```bash
export BRIGHT_DATA_API_KEY="26ca0b85-c197-4f30-8b44-acb65771f482"
```

### 2. Import Errors
**Problem:** `ModuleNotFoundError: No module named 'google_scholar_research_agent'`
**Solution:** Ensure you're in the correct directory with the agent file

### 3. Network Timeouts
**Problem:** `Request exception: timeout`
**Solution:** Increase timeout or check network connectivity
```python
agent.configure_bright_data_api(
    request_timeout=120,  # Increase timeout
    max_retries=5         # More retries
)
```

### 4. CAPTCHA Still Detected
**Problem:** `🔒 CAPTCHA/block detected in response`
**Solutions:**
- Check if your API key has sufficient credits
- Try different zones: `web_unlocker1`, `static_residential`
- Add delays between requests
- Contact Bright Data support

### 5. No Papers Found
**Problem:** `❌ No papers found via Bright Data`
**Debugging:**
```python
# Enable debug logging to see content
import logging
logging.basicConfig(level=logging.DEBUG)

# Check raw content
result = agent._make_bright_data_request("https://scholar.google.com/scholar?q=test")
print(result['content'][:1000])  # Check first 1000 characters
```

## 🔧 Advanced Configuration

### Custom Headers
```python
# Add custom headers for specific use cases
headers = {
    'User-Agent': 'Mozilla/5.0 (compatible; ResearchBot/1.0)',
    'Accept-Language': 'en-US,en;q=0.9'
}

result = agent._make_bright_data_request(
    url="https://scholar.google.com/scholar?q=test",
    headers=headers
)
```

### Different Zones
```python
# Try different Bright Data zones
zones = ['web_unlocker1', 'static_residential', 'datacenter']

for zone in zones:
    agent.configure_bright_data_api(zone=zone)
    papers = agent._search_scholar_with_bright_data("test query")
    if papers:
        print(f"✅ Zone {zone} worked!")
        break
```

### Rate Limiting
```python
import time

# Add delays between requests
for query in queries:
    papers = agent._search_scholar_with_bright_data(query)
    time.sleep(5)  # 5 second delay between queries
```

## 📋 Debugging Checklist

Before reporting issues, check:

- [ ] API key is correctly set in environment
- [ ] Internet connectivity is working
- [ ] Bright Data service status (check their status page)
- [ ] Your account has sufficient credits
- [ ] Debug logging is enabled
- [ ] Test with simple requests first
- [ ] Check the generated log files
- [ ] Verify the agent file is in the correct location

## 🆘 Getting Help

### Log Files
Debug scripts create detailed log files:
- Format: `bright_data_debug_YYYYMMDD_HHMMSS.log`
- Contains full request/response details
- Include relevant portions when reporting issues

### Debugging Commands
```bash
# 1. Quick connectivity test
python -c "
import requests
response = requests.post('https://api.brightdata.com/request', 
    json={'zone': 'web_unlocker1', 'url': 'https://httpbin.org/ip', 'format': 'raw'},
    headers={'Authorization': 'Bearer 26ca0b85-c197-4f30-8b44-acb65771f482', 'Content-Type': 'application/json'},
    timeout=30)
print(f'Status: {response.status_code}, Content: {response.text[:200]}')
"

# 2. Test Google Scholar access
python -c "
from google_scholar_research_agent import GoogleScholarResearchAgent
import os
os.environ['BRIGHT_DATA_API_KEY'] = '26ca0b85-c197-4f30-8b44-acb65771f482'
agent = GoogleScholarResearchAgent()
agent.configure_bright_data_api(enable_bright_data=True)
papers = agent._search_scholar_with_bright_data('test')
print(f'Found {len(papers) if papers else 0} papers')
"
```

Your Bright Data API integration is now fully debugged and ready to use! 🎉 